import json
import os
import random
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

# ---------------- NEW IMPORTS FOR DATABASE ----------------
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

# ---------------- MIGRATE IMPORTS ----------------
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
if not app.secret_key:
    raise ValueError("No SECRET_KEY set for Flask application")

# ---------------- DATABASE SETUP ----------------
# Format: mysql+pymysql://username:password@host:port/database
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("No DATABASE_URL set for Flask application")
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# -------------------------------------------------
#                DATABASE MODELS
# -------------------------------------------------
class DBExercise(db.Model):
    __tablename__ = "exercises"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(10))
    topic = db.Column(db.String(50))

class DBProduct(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)  # Renamed from 'desc'
    category = db.Column(db.String(50))

class DBUser(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    public_name = db.Column(db.String(100))
    birthday = db.Column(db.String(20))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(100))
    profile_photo = db.Column(db.String(200))
    location = db.Column(db.String(100))
    bio = db.Column(db.Text)
    weight = db.Column(db.String(20))
    height = db.Column(db.String(20))
    selected_plan = db.Column(db.String(20))  # e.g., 'ppl', 'ab', etc.
    workout_data = db.Column(db.Text)  # Removed default value


    def verify_password(self, password_plaintext):
        return self.password == password_plaintext# -------------------------------------------------
#  HELPER FUNCTIONS: DB ROW -> DICTIONARY
# -------------------------------------------------
def exercise_to_dict(row: DBExercise):
    return {
        "id": row.id,
        "name": row.name,
        "category": row.category,
        "topic": row.topic
    }

def product_to_dict(row: DBProduct):
    return {
        "id": row.id,
        "name": row.name,
        "price": row.price,
        "description": row.description,  # Updated
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
        "location": row.location,
        "bio": row.bio,
        "weight": row.weight,
        "height": row.height,
        "selected_plan": row.selected_plan,
        "workout_data": json.loads(row.workout_data) if row.workout_data else {},
    }

# -------------------------------------------------
#               LOADING / SAVING DATA
#      (These keep the same function names but use DB)
# -------------------------------------------------
def load_exercises():
    rows = DBExercise.query.all()
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
            password=u['password'],
            public_name=u.get('public_name', ""),
            birthday=u.get('birthday', ""),
            phone=u.get('phone', ""),
            email=u.get('email', ""),
            profile_photo=u.get('profile_photo', ""),
            location=u.get('location', ""),
            bio=u.get('bio', ""),
            weight=u.get('weight', ""),
            height=u.get('height', ""),
            selected_plan=u.get('selected_plan', None),
            workout_data=json.dumps(w_data)
        )
        db.session.add(db_user)
    db.session.commit()

# -------------------------------------------------
#              USER MANAGEMENT (DB)
# -------------------------------------------------
def find_user(username):
    row = DBUser.query.filter_by(username=username).first()
    return user_to_dict(row) if row else None

def authenticate_user(username, password):
    row = DBUser.query.filter_by(username=username).first()
    if row and row.verify_password(password):
        return user_to_dict(row)
    return None

def register_user(username, password, public_name, birthday, phone, email, profile_photo, location, bio, weight, height):
    existing = DBUser.query.filter_by(username=username).first()
    if existing:
        return False
    db_user = DBUser(
        username=username,
        public_name=public_name,
        password=password,
        birthday=birthday,
        phone=phone,
        email=email,
        profile_photo=profile_photo,
        location=location,
        bio=bio,
        weight=weight,
        height=height,
        selected_plan=None,
        workout_data=json.dumps({}),
    )
    db.session.add(db_user)
    db.session.commit()
    return True

def update_user_workout(username, plan_type, plan_data):
    row = DBUser.query.filter_by(username=username).first()
    if row:
        try:
            print(f"Updating user {username} with plan {plan_type}")  # Debugging
            row.selected_plan = plan_type
            row.workout_data = json.dumps(plan_data)
            db.session.commit()
            print("Update successful")  # Debugging
        except Exception as e:
            print(f"Error updating workout for user {username}: {e}")  # Debugging
            db.session.rollback()
    else:
        print(f"User {username} not found")  # Debugging


def update_user_profile(username, public_name, phone, email, birthday, profile_photo, location, bio, weight, height):
    row = DBUser.query.filter_by(username=username).first()
    if row:
        row.public_name = public_name
        row.phone = phone
        row.email = email
        row.birthday = birthday
        row.profile_photo = profile_photo
        row.location = location
        row.bio = bio
        row.weight = weight
        row.height = height
        db.session.commit()

# -------------------------------------------------
#       HELPER FUNCTIONS FOR WORKOUT LOGIC
# -------------------------------------------------
def get_exercise_by_name(exercises, name):
    for ex in exercises:
        if ex['name'].lower() == name.lower():
            return ex
    return None

def pick_one_from_pair(exercises, name1, name2):
    chosen_name = random.choice([name1, name2])
    exercise = get_exercise_by_name(exercises, chosen_name)
    if not exercise:
        flash(f"Exercise '{chosen_name}' not found in the exercise library.")
    return exercise

# -------------------------------------------------
# FULL BODY PLAN
# -------------------------------------------------
def generate_full_body_plan(ex):
    def single():
        w = []
        # chest => smith machine incline + 1 random
        chest_main = get_exercise_by_name(ex, "Smith Machine Incline Bench Press")
        if chest_main:
            w.append(chest_main)
            chest_pool = [c for c in ex if c['topic'].lower() == 'chest' and c['name'] != chest_main['name']]
            if chest_pool:
                selected = random.choice(chest_pool)
                w.append(selected)

        # back => 1 of (pull ups,pully), 1 of (smith machine rows,t-bar row)
        b1 = pick_one_from_pair(ex, "Pull Ups", "Pully")
        b2 = pick_one_from_pair(ex, "Smith machine Rows", "T-Bar row")
        if b1:
            w.append(b1)
        if b2:
            w.append(b2)

        # legs => 1 of (calf raises,sitting calf raises), plus smith machine squat
        l1 = pick_one_from_pair(ex, "Calf Raises", "Sitting Calf Raises")
        if l1:
            w.append(l1)
        sq = get_exercise_by_name(ex, "Smith Machine Squat")
        if sq:
            w.append(sq)

        # shoulders => 1 of (sitting lateral,cable lateral), plus shoulder press
        s1 = pick_one_from_pair(ex, "Sitting Lateral raise", "Cable Lateral raise")
        sp = get_exercise_by_name(ex, "Shoulder Press")
        if s1:
            w.append(s1)
        if sp:
            w.append(sp)

        # bicep => cable curl
        bc = get_exercise_by_name(ex, "Cable Curl")
        if bc:
            w.append(bc)

        # tricep => cable tricep pushdown
        tri = get_exercise_by_name(ex, "Cable tricep pushdown")
        if tri:
            w.append(tri)

        final = [f"{x['name']} - 3 sets" for x in w if x]
        return final

    return {
        "Monday": single(),
        "Wednesday": single(),
        "Friday": single()
    }

# -------------------------------------------------
# A/B PLAN
# -------------------------------------------------
import random

def generate_ab_plan(ex):
    def workout_A():
        w = []

        # Chest (3 exercises, 3 sets each)
        cm = get_exercise_by_name(ex, "Smith Machine Incline Bench Press")
        if cm:
            w.append(f"{cm['name']} - 3 sets")

        chest_pool = [c for c in ex if c['topic'].lower() == 'chest' and c['name'] != cm['name']]
        if len(chest_pool) >= 2:
            selected_chest = random.sample(chest_pool, 2)
            w.extend([f"{c['name']} - 3 sets" for c in selected_chest])

        # Shoulders (2 exercises: 1 with 4 sets, 1 with 3 sets)
        shoulder_pair = pick_one_from_pair(ex, "Dumbbell Lateral raise", "Sitting Lateral raise")
        if shoulder_pair:
            w.append(f"{shoulder_pair['name']} - 4 sets")

        shoulder_pool = [s for s in ex if s['topic'].lower() == 'shoulders' and s['name'] != shoulder_pair['name']]
        if shoulder_pool:
            selected_shoulder = random.choice(shoulder_pool)
            w.append(f"{selected_shoulder['name']} - 3 sets")

        # Triceps (2 exercises: 1 with 4 sets, 1 with 3 sets)
        tricep_pool = [t for t in ex if t['topic'].lower() == 'triceps']
        if len(tricep_pool) >= 2:
            tricep_main, tricep_secondary = random.sample(tricep_pool, 2)
            w.append(f"{tricep_main['name']} - 4 sets")
            w.append(f"{tricep_secondary['name']} - 3 sets")

        return w

    def workout_B():
        w = []

        # Back (3 exercises, 3 sets each)
        back_pair1 = pick_one_from_pair(ex, "Pull Ups", "Pully")
        back_pair2 = pick_one_from_pair(ex, "Smith machine Rows", "T-Bar row")
        if back_pair1:
            w.append(f"{back_pair1['name']} - 3 sets")
        if back_pair2:
            w.append(f"{back_pair2['name']} - 3 sets")

        back_pool = [bk for bk in ex if bk['topic'].lower() == 'back' and bk['name'] not in [back_pair1['name'] if back_pair1 else None, back_pair2['name'] if back_pair2 else None]]
        if back_pool:
            selected_back = random.choice(back_pool)
            w.append(f"{selected_back['name']} - 3 sets")

        # Legs (3 exercises: 1 with 4 sets, 2 with 3 sets)
        sq = get_exercise_by_name(ex, "Smith Machine Squat")
        if sq:
            w.append(f"{sq['name']} - 4 sets")

        calf_pair = pick_one_from_pair(ex, "Calf Raises", "Sitting Calf Raises")
        if calf_pair:
            w.append(f"{calf_pair['name']} - 3 sets")

        legs_pool = [lg for lg in ex if lg['topic'].lower() == 'legs' and lg['name'] not in [sq['name'], calf_pair['name'] if calf_pair else None]]
        if legs_pool:
            selected_leg = random.choice(legs_pool)
            w.append(f"{selected_leg['name']} - 3 sets")

        # Biceps (2 exercises: 1 with 4 sets, 1 with 3 sets)
        bicep_pool = [b for b in ex if b['topic'].lower() == 'biceps']
        if len(bicep_pool) >= 2:
            bicep_main, bicep_secondary = random.sample(bicep_pool, 2)
            w.append(f"{bicep_main['name']} - 4 sets")
            w.append(f"{bicep_secondary['name']} - 3 sets")

        return w

    return {
        "Sunday": workout_A(),
        "Monday": workout_B(),
        "Wednesday": workout_A(),
        "Thursday": workout_B()
    }

# Helper functions (you should ensure these are properly defined in your code)
def get_exercise_by_name(exercises, name):
    return next((e for e in exercises if e['name'] == name), None)

def pick_one_from_pair(exercises, name1, name2):
    pair = [e for e in exercises if e['name'] in [name1, name2]]
    return random.choice(pair) if pair else None


# -------------------------------------------------
# PPL PLAN
# -------------------------------------------------
def generate_ppl_plan(ex):
    def push_day():
        w = []
        # Chest
        chest_main = get_exercise_by_name(ex, "Smith Machine Incline Bench Press")
        if chest_main:
            w.append({"name": chest_main['name'], "sets": 4})

            chest_secondary = pick_one_from_pair(ex, "Cable Crossover", "Flys")
            if chest_secondary:
                w.append({"name": chest_secondary['name'], "sets": 3})

            # Select a third chest exercise
            chest_pool = [c for c in ex if c['topic'].lower() == 'chest' and c['name'] not in [chest_main['name'], chest_secondary['name']]]
            if chest_pool:
                third_chest = random.choice(chest_pool)
                w.append({"name": third_chest['name'], "sets": 3})

        # Shoulders
        shoulder_main = get_exercise_by_name(ex, "Shoulder Press")
        if shoulder_main:
            w.append({"name": shoulder_main['name'], "sets": 4})

            shoulder_secondary = pick_one_from_pair(ex, "Sitting Lateral raise", "Cable Lateral raise")
            if shoulder_secondary:
                w.append({"name": shoulder_secondary['name'], "sets": 3})

        # Triceps
        tricep_main = get_exercise_by_name(ex, "Cable tricep pushdown")
        if tricep_main:
            w.append({"name": tricep_main['name'], "sets": 4})
            # Assuming there's another tricep exercise like "Overhead Tricep Extension" or "Dips"
            tricep_pool = [t for t in ex if t['topic'].lower() == 'triceps' and t['name'] != tricep_main['name']]
            if tricep_pool:
                tricep_secondary = random.choice(tricep_pool)
                w.append({"name": tricep_secondary['name'], "sets": 4})

        # Formatting
        final = [f"{item['name']} - {item['sets']} sets" for item in w]
        return final

    def pull_day():
        w = []
        # Back
        back_main = get_exercise_by_name(ex, "Smith machine Rows")
        if back_main:
            w.append({"name": back_main['name'], "sets": 3})

        back_option = pick_one_from_pair(ex, "Pull Ups", "Pully")
        if back_option:
            w.append({"name": back_option['name'], "sets": 3})

        # Additional back exercises to make it 4
        back_pool = [b for b in ex if b['topic'].lower() == 'back' and b['name'] not in [back_main['name'], back_option['name'] if back_option else None]]
        for _ in range(2):  # Add up to 2 more exercises
            if back_pool:
                additional_back = random.choice(back_pool)
                w.append({"name": additional_back['name'], "sets": 3})
                back_pool.remove(additional_back)

        # Biceps
        bicep_main = get_exercise_by_name(ex, "Cable Curl")
        if bicep_main:
            w.append({"name": bicep_main['name'], "sets": 3})

            # Select two more bicep exercises
            bicep_pool = [b for b in ex if b['topic'].lower() == 'biceps' and b['name'] != bicep_main['name']]
            for _ in range(2):
                if bicep_pool:
                    additional_bicep = random.choice(bicep_pool)
                    w.append({"name": additional_bicep['name'], "sets": 3})
                    bicep_pool.remove(additional_bicep)

        # Formatting
        final = [f"{item['name']} - {item['sets']} sets" for item in w]
        return final

    def legs_day():
        w = []
        # Legs
        squat = get_exercise_by_name(ex, "Smith Machine Squat")
        if squat:
            w.append({"name": squat['name'], "sets": 4})

        leg_extension = get_exercise_by_name(ex, "Leg Extension")
        if leg_extension:
            w.append({"name": leg_extension['name'], "sets": 3})

        calf = pick_one_from_pair(ex, "Calf Raises", "Sitting Calf Raises")
        if calf:
            w.append({"name": calf['name'], "sets": 3})

        leg_curl = pick_one_from_pair(ex, "Standing Leg Curl", "Leg Curl")
        if leg_curl:
            w.append({"name": leg_curl['name'], "sets": 3})

        # Additional leg exercises to make it 5 or 6
        leg_pool = [lg for lg in ex if lg['topic'].lower() == 'legs' and lg['name'] not in [squat['name'], leg_extension['name'], calf['name'], leg_curl['name'] if leg_curl else None]]
        for _ in range(1):  # Add up to 2 more exercises
            if leg_pool and len(w) < 6:
                additional_leg = random.choice(leg_pool)
                w.append({"name": additional_leg['name'], "sets": 3})
                leg_pool.remove(additional_leg)

        # Adjust sets if total exceeds 17
        total_sets = sum(item['sets'] for item in w)
        if total_sets > 17:
            # Reduce the last added exercise sets to fit
            excess = total_sets - 17
            if w[-1]['sets'] > 3:
                w[-1]['sets'] -= excess
                if w[-1]['sets'] < 3:
                    w[-1]['sets'] = 3

        # Formatting
        final = [f"{item['name']} - {item['sets']} sets" for item in w]
        return final

    return {
        "Monday": push_day(),
        "Tuesday": pull_day(),
        "Wednesday": legs_day(),
        "Friday": push_day(),
        "Saturday": pull_day(),
        "Sunday": legs_day()
    }

# -------------------------------------------------
# NEW A/B/C PLAN
# -------------------------------------------------
def generate_new_abc_plan(ex):
    def workout_A():
        w = []
        # Chest
        chest_main = get_exercise_by_name(ex, "Smith Machine Incline Bench Press")
        if chest_main:
            w.append({"name": chest_main['name'], "sets": 3})

            chest_secondary = pick_one_from_pair(ex, "Flys", "Cable Crossover")
            if chest_secondary:
                w.append({"name": chest_secondary['name'], "sets": 3})

            # Select two more chest exercises
            chest_pool = [c for c in ex if c['topic'].lower() == 'chest' and c['name'] not in [chest_main['name'], chest_secondary['name']]]
            for _ in range(2):
                if chest_pool:
                    additional_chest = random.choice(chest_pool)
                    w.append({"name": additional_chest['name'], "sets": 3})
                    chest_pool.remove(additional_chest)

        # Back
        back_main = get_exercise_by_name(ex, "Smith machine Rows")
        if back_main:
            w.append({"name": back_main['name'], "sets": 3})

            back_option = pick_one_from_pair(ex, "Pull Ups", "Pully")
            if back_option:
                w.append({"name": back_option['name'], "sets": 3})

            # Select two more back exercises
            back_pool = [b for b in ex if b['topic'].lower() == 'back' and b['name'] not in [back_main['name'], back_option['name'] if back_option else None]]
            for _ in range(2):
                if back_pool:
                    additional_back = random.choice(back_pool)
                    w.append({"name": additional_back['name'], "sets": 3})
                    back_pool.remove(additional_back)

        # Formatting
        final = [f"{item['name']} - {item['sets']} sets" for item in w]
        return final

    def workout_B():
        w = []
        # Shoulders
        shoulder_main = get_exercise_by_name(ex, "Shoulder Press")
        if shoulder_main:
            w.append({"name": shoulder_main['name'], "sets": 3})

            shoulder_secondary = pick_one_from_pair(ex, "Sitting Lateral raise", "Cable Lateral raise")
            if shoulder_secondary:
                w.append({"name": shoulder_secondary['name'], "sets": 3})

            # Select one more shoulder exercise
            shoulder_pool = [s for s in ex if s['topic'].lower() == 'shoulder' and s['name'] not in [shoulder_main['name'], shoulder_secondary['name']]]
            if shoulder_pool:
                additional_shoulder = random.choice(shoulder_pool)
                w.append({"name": additional_shoulder['name'], "sets": 3})

        # Biceps
        bicep_main = get_exercise_by_name(ex, "Cable Curl")
        if bicep_main:
            w.append({"name": bicep_main['name'], "sets": 3})

            # Select two more bicep exercises
            bicep_pool = [b for b in ex if b['topic'].lower() == 'biceps' and b['name'] != bicep_main['name']]
            for _ in range(2):
                if bicep_pool:
                    additional_bicep = random.choice(bicep_pool)
                    w.append({"name": additional_bicep['name'], "sets": 3})
                    bicep_pool.remove(additional_bicep)

        # Triceps
        tricep_main = get_exercise_by_name(ex, "Cable tricep pushdown")
        if tricep_main:
            w.append({"name": tricep_main['name'], "sets": 3})

            # Select two more tricep exercises
            tricep_pool = [t for t in ex if t['topic'].lower() == 'triceps' and t['name'] != tricep_main['name']]
            for _ in range(2):
                if tricep_pool:
                    additional_tricep = random.choice(tricep_pool)
                    w.append({"name": additional_tricep['name'], "sets": 3})
                    tricep_pool.remove(additional_tricep)

        # Formatting
        final = [f"{item['name']} - {item['sets']} sets" for item in w]
        return final

    def workout_C():
        w = []
        # Legs
        squat = get_exercise_by_name(ex, "Smith Machine Squat")
        if squat:
            w.append({"name": squat['name'], "sets": 3})

        leg_extension = get_exercise_by_name(ex, "Leg Extension")
        if leg_extension:
            w.append({"name": leg_extension['name'], "sets": 3})

        calf = pick_one_from_pair(ex, "Calf Raises", "Sitting Calf Raises")
        if calf:
            w.append({"name": calf['name'], "sets": 3})

        leg_curl = pick_one_from_pair(ex, "Standing Leg Curl", "Leg Curl")
        if leg_curl:
            w.append({"name": leg_curl['name'], "sets": 3})

        # Select one or two more leg exercises
        leg_pool = [lg for lg in ex if lg['topic'].lower() == 'legs' and lg['name'] not in [squat['name'], leg_extension['name'], calf['name'], leg_curl['name'] if leg_curl else None]]
        for _ in range(2):
            if leg_pool and len(w) < 6:
                additional_leg = random.choice(leg_pool)
                w.append({"name": additional_leg['name'], "sets": 3})
                leg_pool.remove(additional_leg)

        # Formatting
        final = [f"{item['name']} - {item['sets']} sets" for item in w]
        return final

    return {
        "Monday": workout_A(),
        "Tuesday": workout_B(),
        "Wednesday": workout_C(),
        "Friday": workout_A(),
        "Saturday": workout_B(),
        "Sunday": workout_C()
    }

def generate_workout_plan(plan_type):
    ex = load_exercises()
    if plan_type == 'full_body':
        return generate_full_body_plan(ex)
    elif plan_type == 'ab':
        return generate_ab_plan(ex)
    elif plan_type == 'ppl':
        return generate_ppl_plan(ex)
    elif plan_type == 'abc':
        return generate_new_abc_plan(ex)
    else:
        return {}

# -------------------------------------------------
# CART / SHOP
# -------------------------------------------------
def init_cart():
    if 'cart' not in session:
        session['cart'] = []

def add_to_cart(product_id):
    init_cart()
    session['cart'].append(product_id)

def clear_cart():
    session['cart'] = []

# -------------------------------------------------
# FLASK ROUTES
# -------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/my_workout')
def my_workout():
    if 'username' not in session:
        flash("Please log in to see your workout.")
        return redirect(url_for('login'))

    user = find_user(session['username'])
    if not user:
        flash("User not found. Please log in again.")
        return redirect(url_for('logout'))

    plan_type = user.get('selected_plan')
    if not plan_type:
        flash("No workout plan selected yet.")
        return redirect(url_for('choose_plan'))

    plan_data = user.get('workout_data', {})
    return render_template('my_workout.html', plan_type=plan_type, plan=plan_data)

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        public_name = request.form.get('public_name')
        birthday = request.form.get('birthday')
        phone = request.form.get('phone')
        email = request.form.get('email')
        profile_photo = request.form.get('profile_photo')
        location = request.form.get('location')
        bio = request.form.get('bio')
        weight = request.form.get('weight') or ""
        height = request.form.get('height') or ""

        if not username or not password:
            flash("Username & password are required.")
            return redirect(url_for('signup'))

        ok = register_user(username, password, public_name, birthday, phone, email, profile_photo, location, bio, weight, height)
        if ok:
            flash("Signup successful! You can now login.")
            return redirect(url_for('login'))
        else:
            flash("Username already exists. Choose a different one.")
            return redirect(url_for('signup'))
    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = authenticate_user(username, password)
        if user:
            session['username'] = username
            flash("Logged in successfully!")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials.")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for('home'))

@app.route('/choose_plan', methods=['GET','POST'])
def choose_plan():
    if 'username' not in session:
        flash("Please log in first.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        plan_type = request.form.get('plan_type')
        if plan_type:
            new_plan = generate_workout_plan(plan_type)
            update_user_workout(session['username'], plan_type, new_plan)
            flash(f"You selected the {plan_type.upper()} plan!")
            return redirect(url_for('my_workout'))

    plan_options = [
        {"id": "full_body", "label": "Full Body"},
        {"id": "ab",        "label": "A/B"},
        {"id": "ppl",       "label": "Push, Pull, Legs"},
        {"id": "abc",       "label": "A/B/C (New)"}
    ]
    return render_template('choose_plan.html', plan_options=plan_options)

@app.route('/reroll')
def reroll():
    if 'username' not in session:
        flash("Log in first.")
        return redirect(url_for('login'))
    user = find_user(session['username'])
    if not user or not user.get('selected_plan'):
        flash("No plan to re-roll.")
        return redirect(url_for('choose_plan'))

    plan_type = user['selected_plan']
    new_plan = generate_workout_plan(plan_type)
    update_user_workout(user['username'], plan_type, new_plan)
    flash("Your plan has been re-generated!")
    return redirect(url_for('my_workout'))

@app.route('/profile', methods=['GET','POST'])
def profile():
    if 'username' not in session:
        flash("Please log in to view your profile.")
        return redirect(url_for('login'))

    user = find_user(session['username'])
    if not user:
        flash("User not found.")
        return redirect(url_for('home'))

    is_edit_mode = request.args.get('edit', '0') == '1'
    if request.method == 'POST':
        public_name = request.form.get('public_name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        birthday = request.form.get('birthday')
        profile_photo = request.form.get('profile_photo')
        location = request.form.get('location')
        bio = request.form.get('bio')
        weight = request.form.get('weight') or ""
        height = request.form.get('height') or ""

        update_user_profile(user['username'], public_name, phone, email, birthday, profile_photo, location, bio, weight, height)
        flash("Profile updated!")
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user, is_edit_mode=is_edit_mode)

@app.route('/exercise_library')
def exercise_library_all():
    ex = load_exercises()
    muscle_groups = ['Chest', 'Shoulder', 'Triceps', 'Back', 'Biceps', 'Legs']
    return render_template('exercise_library_index.html',
                           exercises=ex,
                           muscle_groups=muscle_groups,
                           current_muscle='all')

@app.route('/exercise_library/<muscle>')
def exercise_library_muscle(muscle):
    ex = load_exercises()
    muscle_groups = ['Chest', 'Shoulder', 'Triceps', 'Back', 'Biceps', 'Legs']
    if muscle.lower() == 'all':
        filtered = ex
    else:
        filtered = [e for e in ex if e['topic'].lower() == muscle.lower()]
    return render_template('exercise_library_index.html',
                           exercises=filtered,
                           muscle_groups=muscle_groups,
                           current_muscle=muscle.capitalize())

@app.route('/exercise/<exercise_name>')
def exercise_detail(exercise_name):
    ex = load_exercises()
    match = None
    for item in ex:
        if item['name'].lower() == exercise_name.lower():
            match = item
            break
    if not match:
        flash("Exercise not found.")
        return redirect(url_for('exercise_library_all'))
    return render_template('exercise_detail.html', exercise=match)

@app.route('/shop')
def shop_index():
    init_cart()
    all_products = load_products()
    categories = sorted({p['category'] for p in all_products})
    return render_template('shop_index.html',
                           products=all_products,
                           categories=categories,
                           current_cat='all')

@app.route('/shop/<cat>')
def shop_category(cat):
    init_cart()
    all_products = load_products()
    categories = sorted({p['category'] for p in all_products})
    if cat.lower() == 'all':
        filtered = all_products
    else:
        filtered = [p for p in all_products if p['category'].lower() == cat.lower()]
    return render_template('shop_index.html',
                           products=filtered,
                           categories=categories,
                           current_cat=cat)

@app.route('/add_to_cart/<int:product_id>')
def add_item_to_cart(product_id):
    add_to_cart(product_id)
    flash("Product added to cart.")
    ref = request.referrer or url_for('shop_index')
    return redirect(ref + "#stay")

@app.route('/cart')
def cart():
    init_cart()
    all_products = load_products()
    items = []
    total = 0
    for pid in session['cart']:
        prod = next((p for p in all_products if p['id'] == pid), None)
        if prod:
            items.append(prod)
            total += prod['price']
    return render_template('cart.html', items=items, total=round(total, 2))

@app.route('/clear_cart')
def clear_cart_route():
    clear_cart()
    flash("Cart cleared.")
    return redirect(url_for('shop_index'))

@app.route('/checkout', methods=['GET','POST'])
def checkout():
    init_cart()
    all_products = load_products()
    items = []
    total = 0
    for pid in session['cart']:
        prod = next((p for p in all_products if p['id'] == pid), None)
        if prod:
            items.append(prod)
            total += prod['price']

    if request.method == 'POST':
        flash("Thank you! Your fake purchase has been processed.")
        return redirect(url_for('cart'))

    return render_template('checkout.html', items=items, total=round(total, 2))

@app.route('/progress')
def progress():
    if 'username' not in session:
        flash("Log in first.")
        return redirect(url_for('login'))
    user = find_user(session['username'])
    if not user:
        flash("User not found.")
        return redirect(url_for('home'))
    return "<h2>Progress Tracking (Coming Soon)</h2>"

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200
# -------------------------------------------------
#   MAIN ENTRY POINT
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

