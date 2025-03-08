import os
from google.cloud import storage
import psutil
from werkzeug.utils import secure_filename
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST
from flask import render_template, request, redirect, url_for, session, flash, jsonify, Flask
from app import app
from app.helpers import (load_exercises, load_products, find_user, authenticate_user, 
                         register_user, update_user_workout, update_user_profile, 
                         init_cart, add_to_cart, clear_cart, hash_text)
from app.workout import generate_workout_plan
import threading
import time

# Define your gauges.
cpu_gauge = Gauge('python_app_cpu_percent', 'Current CPU usage percent')
memory_gauge = Gauge('python_app_memory_percent', 'Current memory usage percent')

def update_metrics():
    while True:
        # Use non-blocking measurement.
        cpu_percent = psutil.cpu_percent(interval=None)
        memory_percent = psutil.virtual_memory().percent

        cpu_gauge.set(cpu_percent)
        memory_gauge.set(memory_percent)

        # Update every second.
        time.sleep(1)

# Start background thread to update metrics.
threading.Thread(target=update_metrics, daemon=True).start()

@app.route('/metrics')
def metrics():
    # Simply return the latest collected metrics.
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}



# --- Google Cloud Storage Settings ---
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
BUCKET_NAME = 'pulsefit-profile-photos'  # Your bucket name

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file_to_gcs(file, filename):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_file(file, content_type=file.content_type)
    blob.make_public()
    return blob.public_url

def delete_file_from_gcs(file_url):
    try:
        # Assumes file_url format: https://storage.googleapis.com/BUCKET_NAME/filename
        filename = file_url.split('/')[-1]
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.delete()
    except Exception as e:
        print("Error deleting file from GCS:", e)

# ------------------------------
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
    exercises = load_exercises()  # Load the full list of exercises from the database
    return render_template('my_workout.html', plan_type=plan_type, plan=plan_data, exercises=exercises)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        public_name = request.form.get('public_name')
        birthday = request.form.get('birthday')
        phone = request.form.get('phone')
        email = request.form.get('email')
        profile_photo = request.form.get('profile_photo')
        cover_photo = request.form.get('cover_photo')
        location = request.form.get('location')
        bio = request.form.get('bio')
        weight = request.form.get('weight') or ""
        height = request.form.get('height') or ""
        if not username or not password:
            flash("Username & password are required.")
            return redirect(url_for('signup'))
        
        # Hash the password before saving it
        hashed_password = hash_text(password)
        
        ok = register_user(username, hashed_password, public_name, birthday, phone, email, profile_photo, cover_photo, location, bio, weight, height)
        if ok:
            flash("Signup successful! You can now login.")
            return redirect(url_for('login'))
        else:
            flash("Username already exists. Choose a different one.")
            return redirect(url_for('signup'))
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('username')  # Can be username or email
        password = request.form.get('password')
        
        # Hash the submitted password
        hashed_password = hash_text(password)
        
        user = authenticate_user(identifier, hashed_password)
        if user:
            session['username'] = user['username']
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

@app.route('/choose_plan', methods=['GET', 'POST'])
def choose_plan():
    if 'username' not in session:
        flash("Please log in first.")
        return redirect(url_for('login'))
    if request.method == 'POST':
        plan_type = request.form.get('plan_type')
        if plan_type:
            if plan_type == "custom":
                return redirect(url_for('custom_plan_setup'))
            else:
                new_plan = generate_workout_plan(plan_type)
                update_user_workout(session['username'], plan_type, new_plan)
                flash(f"You selected the {plan_type.upper()} plan!")
                return redirect(url_for('my_workout'))
    plan_options = [
        {"id": "full_body", "label": "Full Body"},
        {"id": "ab",        "label": "A/B"},
        {"id": "ppl",       "label": "Push, Pull, Legs"},
        {"id": "abc",       "label": "A/B/C"},
        {"id": "custom",    "label": "Custom Workout (New)"}
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

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        flash("Please log in to view your profile.")
        return redirect(url_for('login'))

    user = find_user(session['username'])
    if not user:
        flash("User not found.")
        return redirect(url_for('home'))

    # Fetch the user's workout plan
    plan_type = user.get('selected_plan')
    plan = user.get('workout_data', {})

    if request.method == 'POST':
        # Check for cropped images first; if not present, use the regular inputs.
        if 'cropped_profile_photo' in request.files:
            file = request.files['cropped_profile_photo']
        else:
            file = request.files.get('profile_photo')
            
        if 'cropped_cover_photo' in request.files:
            header_file = request.files['cropped_cover_photo']
        else:
            header_file = request.files.get('header_photo')  # originally "cover_photo" renamed on front end

        # Use current URLs as defaults
        profile_photo_url = user.get('profile_photo')
        cover_photo_url = user.get('cover_photo')  # DB column remains "cover_photo"

        # Process profile photo upload
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if profile_photo_url:
                delete_file_from_gcs(profile_photo_url)
            profile_photo_url = upload_file_to_gcs(file, filename)

        # Process cover (header) photo upload
        if header_file and allowed_file(header_file.filename):
            header_filename = secure_filename(header_file.filename)
            if cover_photo_url:
                delete_file_from_gcs(cover_photo_url)
            cover_photo_url = upload_file_to_gcs(header_file, header_filename)

        # Retrieve other form fields (falling back to existing values)
        public_name = request.form.get('public_name') or user.get('public_name')
        phone = request.form.get('phone') or user.get('phone')
        email = request.form.get('email') or user.get('email')
        birthday = request.form.get('birthday') or user.get('birthday')
        location = request.form.get('location') or user.get('location')
        bio = request.form.get('bio') or user.get('bio')
        weight = request.form.get('weight') or user.get('weight')
        height = request.form.get('height') or user.get('height')

        # Update the user profile in the database
        update_user_profile(
            user['username'],
            public_name=public_name,
            phone=phone,
            email=email,
            birthday=birthday,
            profile_photo_url=profile_photo_url,
            cover_photo_url=cover_photo_url,
            location=location,
            bio=bio,
            weight=weight,
            height=height
        )

        flash("Profile updated!")
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user, plan_type=plan_type, plan=plan)

@app.route('/exercise_library')
def exercise_library_all():
    ex = load_exercises()
    muscle_groups = ['Chest', 'Shoulder', 'Triceps', 'Back', 'Biceps', 'Legs']
    return render_template('exercise_library_index.html', exercises=ex, muscle_groups=muscle_groups, current_muscle='all')

@app.route('/exercise_library/<muscle>')
def exercise_library_muscle(muscle):
    ex = load_exercises()
    muscle_groups = ['Chest', 'Shoulder', 'Triceps', 'Back', 'Biceps', 'Legs']
    if muscle.lower() == 'all':
        filtered = ex
    else:
        filtered = [e for e in ex if e['topic'].lower() == muscle.lower()]
    return render_template('exercise_library_index.html', exercises=filtered, muscle_groups=muscle_groups, current_muscle=muscle.capitalize())

@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'username' not in session:
        flash("Please log in to edit your profile.")
        return redirect(url_for('login'))
    user = find_user(session['username'])
    if not user:
        flash("User not found.")
        return redirect(url_for('home'))
    if request.method == 'POST':
        public_name = request.form.get('public_name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        birthday = request.form.get('birthday')
        file = request.files.get('profile_photo')
        profile_photo_url = user.get('profile_photo')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if profile_photo_url:
                delete_file_from_gcs(profile_photo_url)
            profile_photo_url = upload_file_to_gcs(file, filename)
        cover_file = request.files.get('cover_photo')
        cover_photo_url = user.get('cover_photo')
        if cover_file and allowed_file(cover_file.filename):
            cover_filename = secure_filename(cover_file.filename)
            if cover_photo_url:
                delete_file_from_gcs(cover_photo_url)
            cover_photo_url = upload_file_to_gcs(cover_file, cover_filename)
        location = request.form.get('location')
        bio = request.form.get('bio')
        weight = request.form.get('weight') or ""
        height = request.form.get('height') or ""
        update_user_profile(user['username'], public_name, phone, email, birthday, profile_photo_url, cover_photo_url, location, bio, weight, height)
        flash("Profile updated!")
        return redirect(url_for('profile'))
    return render_template('edit_profile.html', user=user)

@app.route('/exercise/<exercise_name>')
def exercise_detail(exercise_name):
    ex = load_exercises()
    match = next((item for item in ex if item['name'].lower() == exercise_name.lower()), None)
    if not match:
        flash("Exercise not found.")
        return redirect(url_for('exercise_library_all'))
    return render_template('exercise_detail.html', exercise=match)

@app.route('/shop')
def shop_index():
    init_cart()
    all_products = load_products()
    categories = sorted({p['category'] for p in all_products})
    return render_template('shop_index.html', products=all_products, categories=categories, current_cat='all')

@app.route('/shop/<cat>')
def shop_category(cat):
    init_cart()
    all_products = load_products()
    categories = sorted({p['category'] for p in all_products})
    if cat.lower() == 'all':
        filtered = all_products
    else:
        filtered = [p for p in all_products if p['category'].lower() == cat.lower()]
    return render_template('shop_index.html', products=filtered, categories=categories, current_cat=cat)

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

@app.route('/checkout', methods=['GET', 'POST'])
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

@app.route('/custom_plan_setup', methods=['GET', 'POST'])
def custom_plan_setup():
    from app.helpers import load_exercises
    exercises = load_exercises()
    if request.method == 'POST':
        try:
            num_days = int(request.form.get('num_days'))
        except (TypeError, ValueError):
            flash("Invalid number of days.")
            return redirect(url_for('custom_plan_setup'))
        
        if num_days == 3:
            day_names = ["Sunday", "Tuesday", "Thursday"]
        elif num_days == 4:
            day_names = ["Sunday", "Monday", "Wednesday", "Thursday"]
        elif num_days == 5:
            day_names = ["Sunday", "Monday", "Tuesday", "Thursday", "Friday"]
        elif num_days == 6:
            day_names = ["Sunday", "Monday", "Tuesday", "Thursday", "Friday", "Saturday"]
        else:
            day_names = [f"Day {i}" for i in range(1, num_days + 1)]
        
        custom_plan_temp = {}
        for i, day in enumerate(day_names, start=1):
            chosen_str = request.form.get(f'exercises_day_{i}')
            if chosen_str:
                exercises_list = [ex.strip() for ex in chosen_str.split(',') if ex.strip()]
                custom_plan_temp[day] = exercises_list
            else:
                custom_plan_temp[day] = []
        
        session['custom_plan_temp'] = custom_plan_temp
        return redirect(url_for('custom_plan_sets'))
    return render_template('custom_plan_setup.html', exercises=exercises)

@app.route('/custom_plan_sets', methods=['GET', 'POST'])
def custom_plan_sets():
    custom_plan_temp = session.get('custom_plan_temp')
    if not custom_plan_temp:
        flash("No custom plan data found. Please create your custom plan first.")
        return redirect(url_for('custom_plan_setup'))
    if request.method == 'POST':
        final_plan = {}
        for day, exercises in custom_plan_temp.items():
            day_exercises = []
            for idx, ex_name in enumerate(exercises):
                field_name = f"set_count_{day}_{idx}"
                try:
                    count = int(request.form.get(field_name, 3))
                except (TypeError, ValueError):
                    count = 3
                day_exercises.append(f"{ex_name} - {count} sets")
            final_plan[day] = day_exercises
        from app.helpers import update_user_workout
        update_user_workout(session['username'], 'custom', final_plan)
        session.pop('custom_plan_temp', None)
        flash("Custom workout plan generated!")
        return redirect(url_for('my_workout'))
    return render_template('custom_plan_sets.html', custom_plan=custom_plan_temp)
@app.route('/update_exercise', methods=['POST'])
def update_exercise():
    data = request.get_json()
    day = data.get('day')
    old_indices = data.get('oldIndices')  # Expected to be a list of integers (or strings convertible to int)
    new_exercises = data.get('newExercises')  # Expected to be a list of dicts: { "name": "Exercise", "sets": number }

    # Basic validation
    if not day or old_indices is None or new_exercises is None:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    # Retrieve the current user and their workout plan
    user = find_user(session['username'])
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    workout_plan = user.get('workout_data', {})
    if day not in workout_plan:
        return jsonify({'success': False, 'message': 'Day not found in plan'}), 400

    day_workouts = workout_plan.get(day)
    if not isinstance(day_workouts, list):
        return jsonify({'success': False, 'message': 'Invalid day workouts format'}), 400

    # Determine how many exercises to replace based on the smaller array length
    replace_count = min(len(old_indices), len(new_exercises))

    try:
        for i in range(replace_count):
            # Convert index and set count to integers
            idx = int(old_indices[i])
            if idx < 0 or idx >= len(day_workouts):
                return jsonify({'success': False, 'message': f'Invalid exercise index: {idx}'}), 400

            ex_name = new_exercises[i].get('name')
            ex_sets = new_exercises[i].get('sets')
            if not ex_name or ex_sets is None:
                return jsonify({'success': False, 'message': 'Missing name or sets in newExercises'}), 400

            ex_sets = int(ex_sets)
            if ex_sets < 1:
                ex_sets = 1

            # Replace the exercise at the given index with the new exercise
            day_workouts[idx] = f"{ex_name} - {ex_sets} sets"
    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'message': str(e)}), 400

    # Update the workout plan in the database
    workout_plan[day] = day_workouts
    update_user_workout(user['username'], user.get('selected_plan'), workout_plan)
    
    return jsonify({'success': True, 'message': 'Day workout updated'})

