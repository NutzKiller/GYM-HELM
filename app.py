import json
import os
import random
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "CHANGE_ME_TO_SOMETHING_SECRET"

DATA_EXERCISES_FILE = 'exercises.json'
DATA_PRODUCTS_FILE = 'products.json'
DATA_USERS_FILE = 'users.json'

# -------------------------------------------------
#               LOADING / SAVING DATA
# -------------------------------------------------
def load_exercises():
    with open(DATA_EXERCISES_FILE, 'r') as f:
        return json.load(f)

def load_products():
    with open(DATA_PRODUCTS_FILE, 'r') as f:
        return json.load(f)

def load_users():
    if not os.path.exists(DATA_USERS_FILE):
        return []
    with open(DATA_USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(DATA_USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

# -------------------------------------------------
#              USER MANAGEMENT
# -------------------------------------------------
def find_user(username):
    users = load_users()
    for u in users:
        if u['username'] == username:
            return u
    return None

def authenticate_user(username, password):
    user = find_user(username)
    if user and user['password'] == password:
        return user
    return None

def register_user(username, password, public_name, birthday, phone, email, profile_photo, location, bio, weight, height):
    users = load_users()
    if find_user(username) is not None:
        return False

    new_user = {
        "username": username,
        "password": password,
        "public_name": public_name,
        "birthday": birthday,
        "phone": phone,
        "email": email,
        "profile_photo": profile_photo,
        "location": location,
        "bio": bio,
        "weight": weight,
        "height": height,
        "selected_plan": None,
        "workout_data": {}
    }
    users.append(new_user)
    save_users(users)
    return True

def update_user_workout(username, plan_type, plan_data):
    users = load_users()
    for u in users:
        if u['username'] == username:
            u['selected_plan'] = plan_type
            u['workout_data'] = plan_data
            break
    save_users(users)

def update_user_profile(username, public_name, phone, email, birthday, profile_photo, location, bio, weight, height):
    users = load_users()
    for u in users:
        if u['username'] == username:
            u['public_name'] = public_name
            u['phone'] = phone
            u['email'] = email
            u['birthday'] = birthday
            u['profile_photo'] = profile_photo
            u['location'] = location
            u['bio'] = bio
            u['weight'] = weight
            u['height'] = height
            break
    save_users(users)

# -------------------------------------------------
#         WORKOUT PLAN GENERATION LOGIC
# -------------------------------------------------
def get_exercise_by_name(exercises, name):
    for ex in exercises:
        if ex['name'].lower() == name.lower():
            return ex
    return None

def pick_one_from_pair(exercises, name1, name2):
    chosen_name = random.choice([name1, name2])
    return get_exercise_by_name(exercises, chosen_name)

def generate_full_body_plan(ex):
    def single():
        w = []
        c_main = get_exercise_by_name(ex, "Smith Machine Incline Bench Press")
        if c_main: w.append(c_main)
        chest_pool = [i for i in ex if i['topic']=='chest' and c_main and i['name']!=c_main['name']]
        if chest_pool:
            w.append(random.choice(chest_pool))
        # back
        b1 = pick_one_from_pair(ex, "Pull Ups","Pully")
        b2 = pick_one_from_pair(ex, "Smith machine Rows","T-Bar row")
        if b1: w.append(b1)
        if b2: w.append(b2)
        # legs
        l1 = pick_one_from_pair(ex, "Calf Raises","Sitting Calf Raises")
        if l1: w.append(l1)
        sq = get_exercise_by_name(ex, "Smith Machine Squat")
        if sq: w.append(sq)
        # shoulders
        s1 = pick_one_from_pair(ex, "Sitting Lateral raise","Cable Lateral raise")
        sp = get_exercise_by_name(ex, "Shoulder Press")
        if s1: w.append(s1)
        if sp: w.append(sp)
        # biceps
        bc = get_exercise_by_name(ex, "Cable Curl")
        if bc: w.append(bc)
        # triceps
        tr = get_exercise_by_name(ex, "Cable tricep pushdown")
        if tr: w.append(tr)
        return [f"{i['name']} - 3 sets" for i in w if i]

    return {
        "Monday": single(),
        "Wednesday": single(),
        "Friday": single()
    }

def generate_ab_plan(ex):
    def genA():
        w=[]
        cm = get_exercise_by_name(ex, "Smith Machine Incline Bench Press")
        if cm: w.append(cm)
        c_pair = pick_one_from_pair(ex, "Cable Crossover", "Flys")
        if c_pair: w.append(c_pair)
        chest_pool = [i for i in ex if i['topic']=='chest' 
                      and cm and i['name']!=cm['name']
                      and c_pair and i['name']!=c_pair['name']]
        if chest_pool:
            w.append(random.choice(chest_pool))

        # shoulders
        sp = get_exercise_by_name(ex, "Shoulder Press")
        if sp: w.append(sp)
        s_pair = pick_one_from_pair(ex, "Sitting Lateral raise", "Cable Lateral raise")
        if s_pair: w.append(s_pair)

        # triceps
        tr_main = get_exercise_by_name(ex, "Cable tricep pushdown")
        if tr_main: w.append(tr_main)
        tri_pool = [i for i in ex if i['topic']=='triceps' and tr_main and i['name']!=tr_main['name']]
        if tri_pool:
            w.append(random.choice(tri_pool))
        return [f"{i['name']} - 3 sets" for i in w if i]

    def genB():
        w=[]
        b1 = pick_one_from_pair(ex, "Pull Ups","Pully")
        if b1: w.append(b1)
        b2 = pick_one_from_pair(ex, "Smith machine Rows","T-Bar row")
        if b2: w.append(b2)
        back_pool = [i for i in ex if i['topic']=='back' 
                     and b1 and i['name']!=b1['name']
                     and b2 and i['name']!=b2['name']]
        if back_pool:
            w.append(random.choice(back_pool))
        # legs
        sq = get_exercise_by_name(ex, "Smith Machine Squat")
        if sq: w.append(sq)
        calf = pick_one_from_pair(ex, "Calf Raises","Sitting Calf Raises")
        if calf: w.append(calf)
        legs_pool = [i for i in ex if i['topic']=='legs'
                     and sq and i['name']!=sq['name']
                     and calf and i['name']!=calf['name']]
        if legs_pool:
            w.append(random.choice(legs_pool))
        # biceps
        bc_main = get_exercise_by_name(ex, "Cable Curl")
        if bc_main: w.append(bc_main)
        bicep_pool = [i for i in ex if i['topic']=='biceps' and bc_main and i['name']!=bc_main['name']]
        if bicep_pool:
            w.append(random.choice(bicep_pool))

        final=[]
        used_4=False
        for i in w:
            if i and i['topic']=='legs' and not used_4:
                final.append(f"{i['name']} - 4 sets")
                used_4=True
            else:
                final.append(f"{i['name']} - 3 sets")
        return final

    return {
        "Sunday": genA(),
        "Monday": genB(),
        "Wednesday": genA(),
        "Thursday": genB()
    }

def generate_abc_plan(ex):
    def genA():
        w=[]
        c_main = get_exercise_by_name(ex, "Smith Machine Incline Bench Press")
        c_pair = pick_one_from_pair(ex, "Cable Crossover","Flys")
        if c_main: w.append(c_main)
        if c_pair: w.append(c_pair)
        c_pool = [i for i in ex if i['topic']=='chest'
                  and c_main and i['name']!=c_main['name']
                  and c_pair and i['name']!=c_pair['name']]
        if c_pool:
            w.append(random.choice(c_pool))

        sp = get_exercise_by_name(ex, "Shoulder Press")
        if sp: w.append(sp)
        s_pair = pick_one_from_pair(ex, "Sitting Lateral raise","Cable Lateral raise")
        if s_pair: w.append(s_pair)

        t_main = get_exercise_by_name(ex, "Cable tricep pushdown")
        tri_pool = [i for i in ex if i['topic']=='triceps'
                    and t_main and i['name']!=t_main['name']]
        if t_main: w.append(t_main)
        if tri_pool:
            w.append(random.choice(tri_pool))

        chest_list = w[:3]
        shoulder_list = w[3:5]
        tri_list = w[5:]

        final=[]
        # chest
        if len(chest_list)==3:
            c_4 = random.choice(chest_list)
            for c in chest_list:
                if c == c_4: final.append(f"{c['name']} - 4 sets")
                else: final.append(f"{c['name']} - 3 sets")
        else:
            for c in chest_list:
                final.append(f"{c['name']} - 3 sets")

        # shoulders
        if len(shoulder_list)==2:
            s_4 = random.choice(shoulder_list)
            for s in shoulder_list:
                if s==s_4: final.append(f"{s['name']} - 4 sets")
                else: final.append(f"{s['name']} - 3 sets")
        else:
            for s in shoulder_list:
                final.append(f"{s['name']} - 3 sets")

        # triceps
        for t in tri_list:
            final.append(f"{t['name']} - 4 sets")

        return final

    def genB():
        w=[]
        b1 = pick_one_from_pair(ex, "Pull Ups","Pully")
        b2 = get_exercise_by_name(ex, "Smith machine Rows")
        if b1: w.append(b1)
        if b2: w.append(b2)
        back_pool = [i for i in ex if i['topic']=='back'
                     and b1 and i['name']!=b1['name']
                     and b2 and i['name']!=b2['name']]
        w.extend(random.sample(back_pool, min(2,len(back_pool))))

        bc_main = get_exercise_by_name(ex, "Cable Curl")
        if bc_main:
            w.append(bc_main)
        bicep_pool = [i for i in ex if i['topic']=='biceps'
                      and bc_main and i['name']!=bc_main['name']]
        w.extend(random.sample(bicep_pool, min(2,len(bicep_pool))))

        return [f"{i['name']} - 3 sets" for i in w if i]

    def genC():
        w=[]
        sq = get_exercise_by_name(ex, "Smith Machine Squat")
        calf = pick_one_from_pair(ex, "Calf Raises","Sitting Calf Raises")
        lc = pick_one_from_pair(ex, "Standing Leg Curl","Leg Curl")
        if sq: w.append(sq)
        if calf: w.append(calf)
        if lc: w.append(lc)

        legs_pool = [i for i in ex if i['topic']=='legs'
                     and sq and i['name']!=sq['name']
                     and calf and i['name']!=calf['name']
                     and lc and i['name']!=lc['name']]

        how_many = random.choice([2,3])
        extra = random.sample(legs_pool, min(how_many,len(legs_pool)))
        w.extend(extra)

        sets_arr=[3]*len(w)
        total = 3*len(w)
        if total>17:
            idx = random.randint(0,len(w)-1)
            sets_arr[idx]=2
            total-=1
        else:
            while total<17:
                idx = random.randint(0,len(w)-1)
                if sets_arr[idx]<4:
                    sets_arr[idx]+=1
                    total+=1
                if total==17: break

        final=[]
        for exi, st in zip(w, sets_arr):
            final.append(f"{exi['name']} - {st} sets")
        return final

    return {
        "Monday": genA(),
        "Tuesday": genB(),
        "Wednesday": genC(),
        "Friday": genA(),
        "Saturday": genB(),
        "Sunday": genC()
    }

def generate_workout_plan(plan_type):
    ex = load_exercises()
    if plan_type=='full_body':
        return generate_full_body_plan(ex)
    elif plan_type=='ab':
        return generate_ab_plan(ex)
    elif plan_type=='abc':
        return generate_abc_plan(ex)
    return {}

# -------------------------------------------------
#                  CART LOGIC
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
#                 FLASK ROUTES
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
        flash("No workout plan selected. Please choose one.")
        return redirect(url_for('choose_plan'))

    plan = user.get('workout_data', {})
    return render_template('my_workout.html', plan_type=plan_type, plan=plan)

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method=='POST':
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
            flash("Account created successfully! Please log in.")
            return redirect(url_for('login'))
        else:
            flash("That username is already taken.")
            return redirect(url_for('signup'))
    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
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
        flash("Log in first.")
        return redirect(url_for('login'))
    if request.method=='POST':
        plan_type = request.form.get('plan_type')
        if plan_type:
            plan_data = generate_workout_plan(plan_type)
            update_user_workout(session['username'], plan_type, plan_data)
            flash(f"{plan_type.upper()} plan selected!")
            return redirect(url_for('my_workout'))
    return render_template('choose_plan.html')

@app.route('/reroll')
def reroll():
    if 'username' not in session:
        flash("Log in first.")
        return redirect(url_for('login'))
    user = find_user(session['username'])
    if not user or not user.get('selected_plan'):
        flash("No plan to re-roll. Choose one first.")
        return redirect(url_for('choose_plan'))

    new_plan = generate_workout_plan(user['selected_plan'])
    update_user_workout(user['username'], user['selected_plan'], new_plan)
    flash("Workout re-rolled!")
    return redirect(url_for('my_workout'))

@app.route('/profile', methods=['GET','POST'])
def profile():
    if 'username' not in session:
        flash("Log in to view profile.")
        return redirect(url_for('login'))

    user = find_user(session['username'])
    if not user:
        flash("User not found.")
        return redirect(url_for('home'))

    is_edit_mode = request.args.get('edit','0') == '1'
    if request.method=='POST':
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
        flash("Profile updated.")
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user, is_edit_mode=is_edit_mode)

# ------------------------------
#  EXERCISE LIBRARY with Subnav
# ------------------------------
@app.route('/exercise_library')
def exercise_library_all():
    """
    'All' exercises in one page, subnav for each muscle group
    """
    ex = load_exercises()
    muscle_groups = ['chest','shoulder','triceps','back','biceps','legs']
    return render_template('exercise_library_index.html',
                           exercises=ex,
                           muscle_groups=muscle_groups,
                           current_muscle='all')

@app.route('/exercise_library/<muscle>')
def exercise_library_muscle(muscle):
    """
    Filter exercises by muscle group, or show all if muscle='all'
    """
    ex = load_exercises()
    muscle_groups = ['chest','shoulder','triceps','back','biceps','legs']
    if muscle.lower() == 'all':
        filtered = ex
    else:
        filtered = [e for e in ex if e['topic'].lower() == muscle.lower()]
    return render_template('exercise_library_index.html',
                           exercises=filtered,
                           muscle_groups=muscle_groups,
                           current_muscle=muscle)

@app.route('/exercise/<exercise_name>')
def exercise_detail(exercise_name):
    ex = load_exercises()
    match = None
    for e in ex:
        if e['name'].lower() == exercise_name.lower():
            match = e
            break
    if not match:
        flash("Exercise not found.")
        return redirect(url_for('exercise_library_all'))
    return render_template('exercise_detail.html', exercise=match)

# -----------
#  SHOP SUBNAV
# -----------
@app.route('/shop')
def shop_index():
    """
    /shop => show all products
    Also has subnav with categories
    """
    init_cart()
    all_products = load_products()
    categories = sorted({p['category'] for p in all_products})
    return render_template('shop_index.html',
                           products=all_products,
                           categories=categories,
                           current_cat='all')

@app.route('/shop/<cat>')
def shop_category(cat):
    """
    /shop/<cat> => show only products in that category or all if cat='all'
    """
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
    return redirect(url_for('shop_index'))

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
        # user "submits" the order
        flash("Thank you! Your fake purchase has been processed.")
        return redirect(url_for('cart')) 

    return render_template('checkout.html', items=items, total=round(total, 2))

# Optional progress route
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

if __name__=="__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
