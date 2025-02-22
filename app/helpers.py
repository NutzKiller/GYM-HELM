# app/helpers.py
import json
from flask import session, flash
from app.models import DBExercise, DBProduct, DBUser
from app import db
from sqlalchemy import or_  # Added for authenticate_user
import hashlib


def hash_text(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def exercise_to_dict(row: DBExercise):
    return {
        "id": row.id,
        "name": row.name,
        "category": row.category,
        "topic": row.topic,
        "youtube_video_url": row.youtube_video_url,  # Include the full URL
        "description": row.description,              # NEW: Include description
        "how_to": row.how_to,                         # NEW: Include how_to
        "trainer_id": row.trainer_id,
    }

def product_to_dict(row: DBProduct):
    return {
        "id": row.id,
        "name": row.name,
        "price": row.price,
        "description": row.description,
        "category": row.category
    }

def user_to_dict(row: DBUser):
    return {
        "id": row.id,
        "username": row.username,
        "public_name": row.public_name,
        "birthday": row.birthday,
        "phone": row.phone,
        "email": row.email,
        "profile_photo": row.profile_photo,
        "cover_photo": row.cover_photo if hasattr(row, 'cover_photo') else "",  # NEW: Include cover_photo if exists
        "location": row.location,
        "bio": row.bio,
        "weight": row.weight,
        "height": row.height,
        "selected_plan": row.selected_plan,
        "workout_data": json.loads(row.workout_data) if row.workout_data else {},
        "trainer_id": row.trainer_id
    }

# Data loading functions
def load_exercises():
    rows = []
    ti = None

    if 'username' in session:
        user = find_user(session['username'])  # Returns a dict
        if user and user.get('trainer_id'):  # Use get() to prevent key errors
            ti = find_user_by_id(user.get('trainer_id'))

    if ti:  # If a trainer exists, load their exercises
        rows += DBExercise.query.filter_by(trainer_id=ti.id).all()

    # Always fetch exercises for trainer_id=0 unless they are already included
    if not ti or ti.id != 0:
        rows += DBExercise.query.filter_by(trainer_id=0).all()

    return [exercise_to_dict(r) for r in rows]




def load_products():
    rows = DBProduct.query.all()
    return [product_to_dict(r) for r in rows]

def load_users():
    rows = DBUser.query.all()
    return [user_to_dict(r) for r in rows]

def save_users(users):
    db.session.query(DBUser).delete()  # Clear table
    for u in users:
        w_data = u.get('workout_data', {})
        db_user = DBUser(
            username=u['username'],
            password=hash_text(u['password']),
            public_name=u.get('public_name', ""),
            birthday=u.get('birthday', ""),
            phone=u.get('phone', ""),
            email=u.get('email', ""),
            profile_photo=u.get('profile_photo', ""),
            cover_photo=u.get('cover_photo', ""),  # NEW: cover_photo field
            location=u.get('location', ""),
            bio=u.get('bio', ""),
            weight=u.get('weight', ""),
            height=u.get('height', ""),
            selected_plan=u.get('selected_plan', None),
            workout_data=json.dumps(w_data)
        )
        db.session.add(db_user)
    db.session.commit()

def find_user(username):
    row = DBUser.query.filter_by(username=username).first()
    return user_to_dict(row) if row else None


def find_user_by_id(id):  # Fixed missing colon
    return DBUser.query.filter_by(id=id).first()  # Returns DBUser object or None


def authenticate_user(identifier, password):
    # Updated to allow login with either username or email
    row = DBUser.query.filter(
        or_(DBUser.username == identifier, DBUser.email == identifier)
    ).first()
    if row and row.verify_password(hash_text(password)):
        return user_to_dict(row)
    return None

def register_user(username, password, public_name, birthday, phone, email, profile_photo, cover_photo, location, bio, weight, height):
    existing = DBUser.query.filter_by(username=username).first()
    if existing:
        return False
    db_user = DBUser(
        username=username,
        public_name=public_name,
        password=hash_text(password),
        birthday=birthday,
        phone=phone,
        email=email,
        profile_photo=profile_photo,
        cover_photo=cover_photo,  # NEW: default cover_photo as empty
        location=location,
        bio=bio,
        weight=weight,
        height=height,
        selected_plan=None,
        workout_data=json.dumps({})
    )
    db.session.add(db_user)
    db.session.commit()
    return True

def update_user_workout(username, plan_type, plan_data):
    row = DBUser.query.filter_by(username=username).first()
    if row:
        try:
            row.selected_plan = plan_type
            row.workout_data = json.dumps(plan_data)
            db.session.commit()
        except Exception as e:
            print(f"Error updating workout for user {username}: {e}")
            db.session.rollback()
    else:
        print(f"User {username} not found")

def update_user_profile(username, public_name, phone, email, birthday, profile_photo_url, cover_photo_url, location, bio, weight, height):
    row = DBUser.query.filter_by(username=username).first()
    if row:
        row.public_name = public_name
        row.phone = phone
        row.email = email
        row.birthday = birthday
        row.profile_photo = profile_photo_url
        row.cover_photo = cover_photo_url
        row.location = location
        row.bio = bio
        row.weight = weight
        row.height = height
        db.session.commit()

# Cart functions
def init_cart():
    if 'cart' not in session:
        session['cart'] = []

def add_to_cart(product_id):
    init_cart()
    session['cart'].append(product_id)

def clear_cart():
    session['cart'] = []