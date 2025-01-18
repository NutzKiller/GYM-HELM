import json
import os
import random
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "CHANGE_ME_TO_SOMETHING_SECURE"

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
#       HELPER FUNCTIONS FOR WORKOUT LOGIC
# -------------------------------------------------
def get_exercise_by_name(exercises, name):
    for ex in exercises:
        if ex['name'].lower() == name.lower():
            return ex
    return None

def pick_one_from_pair(exercises, name1, name2):
    chosen_name = random.choice([name1, name2])
    return get_exercise_by_name(exercises, chosen_name)

# -------------------------------------------------
# FULL BODY PLAN
# -------------------------------------------------
def generate_full_body_plan(ex):
    def single():
        w = []
        # chest => smith machine incline + 1 random
        chest_main = get_exercise_by_name(ex, "Smith Machine Incline Bench Press")
        if chest_main: w.append(chest_main)
        chest_pool = [c for c in ex if c['topic']=='chest' and c['name'] != chest_main['name']]
        if chest_pool:
            w.append(random.choice(chest_pool))

        # back => 1 of (pull ups,pully), 1 of (smith machine rows,t-bar row)
        b1 = pick_one_from_pair(ex, "Pull Ups","Pully")
        b2 = pick_one_from_pair(ex, "Smith machine Rows","T-Bar row")
        if b1: w.append(b1)
        if b2: w.append(b2)

        # legs => 1 of (calf raises,sitting calf raises), plus smith machine squat
        l1 = pick_one_from_pair(ex, "Calf Raises","Sitting Calf Raises")
        if l1: w.append(l1)
        sq = get_exercise_by_name(ex, "Smith Machine Squat")
        if sq: w.append(sq)

        # shoulders => 1 of (sitting lateral,cable lateral), plus shoulder press
        s1 = pick_one_from_pair(ex, "Sitting Lateral raise","Cable Lateral raise")
        sp = get_exercise_by_name(ex, "Shoulder Press")
        if s1: w.append(s1)
        if sp: w.append(sp)

        # bicep => cable curl
        bc = get_exercise_by_name(ex, "Cable Curl")
        if bc: w.append(bc)

        # tricep => cable tricep pushdown
        tri = get_exercise_by_name(ex, "Cable tricep pushdown")
        if tri: w.append(tri)

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
def generate_ab_plan(ex):
    def workout_A():
        w = []
        # chest(3)
        cm = get_exercise_by_name(ex, "Smith Machine Incline Bench Press")
        if cm: w.append(cm)
        chest_pair = pick_one_from_pair(ex, "Cable Crossover","Flys")
        if chest_pair: w.append(chest_pair)
        chest_pool = [c for c in ex if c['topic']=='chest' and c['name'] not in [cm['name'], chest_pair['name']]]
        if chest_pool:
            w.append(random.choice(chest_pool))

        # shoulders(2)
        sp = get_exercise_by_name(ex, "Shoulder Press")
        if sp: w.append(sp)
        s_pair = pick_one_from_pair(ex, "Sitting Lateral raise","Cable Lateral raise")
        if s_pair: w.append(s_pair)

        # tricep(2)
        tri_main = get_exercise_by_name(ex, "Cable tricep pushdown")
        if tri_main: w.append(tri_main)
        tri_pool = [t for t in ex if t['topic']=='triceps' and t['name'] != tri_main['name']]
        if tri_pool:
            w.append(random.choice(tri_pool))

        final = [f"{x['name']} - 3 sets" for x in w if x]
        return final

    def workout_B():
        w = []
        # back(3)
        b1 = pick_one_from_pair(ex, "Pull Ups","Pully")
        b2 = pick_one_from_pair(ex, "Smith machine Rows","T-Bar row")
        if b1: w.append(b1)
        if b2: w.append(b2)
        back_pool = [bk for bk in ex if bk['topic']=='back' and bk['name'] not in [b1['name'], b2['name']]]
        if back_pool:
            w.append(random.choice(back_pool))

        # legs(3 => 1 w/4 sets, 2 w/3 sets)
        sq = get_exercise_by_name(ex, "Smith Machine Squat")
        if sq: w.append(sq)
        calf = pick_one_from_pair(ex, "Calf Raises","Sitting Calf Raises")
        if calf: w.append(calf)
        legs_pool = [lg for lg in ex if lg['topic']=='legs' and lg['name'] not in [sq['name'], calf['name']]]
        if legs_pool:
            w.append(random.choice(legs_pool))

        # bicep(2 => must contain cable curl)
        bc_main = get_exercise_by_name(ex, "Cable Curl")
        if bc_main: w.append(bc_main)
        bicep_pool = [b for b in ex if b['topic']=='biceps' and b['name'] != bc_main['name']]
        if bicep_pool:
            w.append(random.choice(bicep_pool))

        final=[]
        used_4=False
        for item in w:
            if item and item['topic']=='legs' and not used_4:
                final.append(f"{item['name']} - 4 sets")
                used_4=True
            else:
                final.append(f"{item['name']} - 3 sets")
        return final

    return {
        "Sunday": workout_A(),
        "Monday": workout_B(),
        "Wednesday": workout_A(),
        "Thursday": workout_B()
    }

# -------------------------------------------------
# PPL => old "a/b/c"
# -------------------------------------------------
def generate_ppl_plan(ex):
    """
    6 workouts => 2 of each (A,B,C).
    A => chest(3 ex => 1x4 sets + 2x3 sets), shoulders(2 => 1x4 +1x3), tricep(2 =>4 sets each)
    B => back(4 =>3 sets), bicep(3 =>3 sets)
    C => legs(5/6 =>3-4 sets, total <=17)
    with the fixed constraints
    """
    def genA():
        w=[]
        # chest
        c_main = get_exercise_by_name(ex, "Smith Machine Incline Bench Press")
        c_pair = pick_one_from_pair(ex, "Cable Crossover","Flys")
        if c_main: w.append(c_main)
        if c_pair: w.append(c_pair)
        c_pool = [ch for ch in ex if ch['topic']=='chest' and ch['name'] not in [c_main['name'], c_pair['name']]]
        if c_pool:
            w.append(random.choice(c_pool))

        # shoulders
        sp = get_exercise_by_name(ex, "Shoulder Press")
        s_pair = pick_one_from_pair(ex, "Sitting Lateral raise","Cable Lateral raise")
        if sp: w.append(sp)
        if s_pair: w.append(s_pair)

        # triceps => 2 => 4 sets each
        t_main = get_exercise_by_name(ex, "Cable tricep pushdown")
        tri_pool = [t for t in ex if t['topic']=='triceps' and t['name']!= t_main['name']]
        tri_list = []
        if t_main: tri_list.append(t_main)
        if tri_pool:
            tri_list.append(random.choice(tri_pool))

        chest_list = w[:3]
        shoulder_list = w[3:5]
        final=[]
        # chest => 1 is 4 sets, 2 are 3 sets
        if len(chest_list)==3:
            c_4 = random.choice(chest_list)
            for c_ in chest_list:
                if c_==c_4:
                    final.append(f"{c_['name']} - 4 sets")
                else:
                    final.append(f"{c_['name']} - 3 sets")
        else:
            for c_ in chest_list:
                final.append(f"{c_['name']} - 3 sets")

        # shoulders => 2 => 1 is 4 sets, 1 is 3 sets
        if len(shoulder_list)==2:
            s_4 = random.choice(shoulder_list)
            for s_ in shoulder_list:
                if s_==s_4:
                    final.append(f"{s_['name']} - 4 sets")
                else:
                    final.append(f"{s_['name']} - 3 sets")
        else:
            for s_ in shoulder_list:
                final.append(f"{s_['name']} - 3 sets")

        # triceps => 2 => 4 sets each
        for tri_ in tri_list:
            final.append(f"{tri_['name']} - 4 sets")

        return final

    def genB():
        w=[]
        # back => 4 => 3 sets
        b1 = pick_one_from_pair(ex, "Pull Ups","Pully")
        sm_r = get_exercise_by_name(ex, "Smith machine Rows")
        if b1: w.append(b1)
        if sm_r: w.append(sm_r)
        back_pool = [bk for bk in ex if bk['topic']=='back' and bk['name'] not in [b1['name'] if b1 else None, sm_r['name'] if sm_r else None]]
        w.extend(random.sample(back_pool, min(2,len(back_pool))))

        # bicep => 3 => 3 sets => must contain cable curl
        bc_main = get_exercise_by_name(ex, "Cable Curl")
        if bc_main: w.append(bc_main)
        bicep_pool = [b for b in ex if b['topic']=='biceps' and b['name']!= bc_main['name']]
        w.extend(random.sample(bicep_pool, min(2,len(bicep_pool))))

        final = [f"{x['name']} - 3 sets" for x in w if x]
        return final

    def genC():
        # legs => 5 or 6 => 3-4 sets, total <=17
        w=[]
        sq = get_exercise_by_name(ex, "Smith Machine Squat")
        if sq: w.append(sq)
        calf = pick_one_from_pair(ex, "Calf Raises","Sitting Calf Raises")
        if calf: w.append(calf)
        lc = pick_one_from_pair(ex, "Standing Leg Curl","Leg Curl")
        if lc: w.append(lc)

        legs_pool = [lg for lg in ex if lg['topic']=='legs' and lg['name'] not in [sq['name'] if sq else None, calf['name'] if calf else None, lc['name'] if lc else None]]
        how_many = random.choice([2,3])
        extra = random.sample(legs_pool, min(how_many,len(legs_pool)))
        w.extend(extra)

        sets_arr=[3]*len(w)
        total=3*len(w)
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
                if total==17:
                    break

        final=[]
        for e_, st in zip(w, sets_arr):
            final.append(f"{e_['name']} - {st} sets")
        return final

    return {
        "Monday": genA(),
        "Tuesday": genB(),
        "Wednesday": genC(),
        "Friday": genA(),
        "Saturday": genB(),
        "Sunday": genC()
    }

# -------------------------------------------------
# NEW A/B/C => now with the correct logic: 
# a => chest(4 ex => 3 sets each), back(4 ex =>3 sets each)
# b => shoulders(3 =>3 sets), bicep(3 =>3 sets), tricep(3 =>3 sets)
# c => legs(5 or 6 =>3 sets each)
# fixed ex for each muscle group
def generate_new_abc_plan(ex):
    def genA():
        w=[]
        # chest(4)
        # always Smith Machine Incline, + exactly 1 of (Flys, Cable Crossover)
        chest_main = get_exercise_by_name(ex, "Smith Machine Incline Bench Press")
        if chest_main: w.append(chest_main)
        chest_pair = pick_one_from_pair(ex, "Flys","Cable Crossover")
        if chest_pair: w.append(chest_pair)
        # we have 2, pick 2 more from chest pool
        chest_pool = [c for c in ex if c['topic']=='chest' and c['name'] not in [chest_main['name'], chest_pair['name']]]
        additional_chest = random.sample(chest_pool, min(2, len(chest_pool)))
        w.extend(additional_chest)

        # back(4)
        # 1 of (pull ups,pully) + 1 of (smith machine rows,t-bar row) => 2
        b1 = pick_one_from_pair(ex, "Pull Ups","Pully")
        b2 = pick_one_from_pair(ex, "Smith machine Rows","T-Bar row")
        if b1: w.append(b1)
        if b2: w.append(b2)
        # pick 2 more from back pool
        back_pool = [bk for bk in ex if bk['topic']=='back' and bk['name'] not in [b1['name'] if b1 else None, b2['name'] if b2 else None]]
        add_back = random.sample(back_pool, min(2, len(back_pool)))
        w.extend(add_back)

        # all 3 sets each
        return [f"{xx['name']} - 3 sets" for xx in w if xx]

    def genB():
        w=[]
        # shoulders(3) => always shoulder press + 1 of (Sitting Lateral or Cable Lateral)
        sp = get_exercise_by_name(ex, "Shoulder Press")
        if sp: w.append(sp)
        s_pair = pick_one_from_pair(ex, "Sitting Lateral raise","Cable Lateral raise")
        if s_pair: w.append(s_pair)
        # we have 2 => pick 1 more from shoulders
        s_pool = [s for s in ex if s['topic']=='shoulder' and s['name'] not in [sp['name'] if sp else None, s_pair['name'] if s_pair else None]]
        if s_pool:
            w.append(random.choice(s_pool))

        # bicep(3) => always Cable Curl => 1 => pick 2 more
        bc_main = get_exercise_by_name(ex, "Cable Curl")
        if bc_main: w.append(bc_main)
        bicep_pool = [b for b in ex if b['topic']=='biceps' and b['name']!= bc_main['name']]
        w.extend(random.sample(bicep_pool, min(2,len(bicep_pool))))

        # tricep(3) => always cable tricep pushdown => 1 => pick 2 more
        tri_main = get_exercise_by_name(ex, "Cable tricep pushdown")
        if tri_main: w.append(tri_main)
        tri_pool = [t for t in ex if t['topic']=='triceps' and t['name']!=tri_main['name']]
        w.extend(random.sample(tri_pool, min(2,len(tri_pool))))

        return [f"{xx['name']} - 3 sets" for xx in w if xx]

    def genC():
        w=[]
        # legs(5 or 6 => 3 sets each)
        # always smith machine squat, leg extention, plus 1 of (standing leg curl or leg curl)
        sq = get_exercise_by_name(ex, "Smith Machine Squat")
        le = get_exercise_by_name(ex, "Leg extention")
        pair_leg = pick_one_from_pair(ex, "Standing Leg Curl","Leg Curl")
        if sq: w.append(sq)
        if le: w.append(le)
        if pair_leg: w.append(pair_leg)

        # we have 3 so far => pick 2 or 3 more => total 5 or 6
        legs_pool = [lg for lg in ex if lg['topic']=='legs' and lg['name'] not in [sq['name'] if sq else None, le['name'] if le else None, pair_leg['name'] if pair_leg else None]]
        how_many_more = random.choice([2,3])
        extra = random.sample(legs_pool, min(how_many_more,len(legs_pool)))
        w.extend(extra)

        final = [f"{xx['name']} - 3 sets" for xx in w if xx]
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
            flash("Signup successful! You can now login.")
            return redirect(url_for('login'))
        else:
            flash("Username already exists. Choose a different one.")
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

    is_edit_mode = request.args.get('edit','0') == '1'
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
    muscle_groups = ['Chest','Shoulder','Triceps','Back','Biceps','Legs']
    return render_template('exercise_library_index.html',
                           exercises=ex,
                           muscle_groups=muscle_groups,
                           current_muscle='all')

@app.route('/exercise_library/<muscle>')
def exercise_library_muscle(muscle):
    ex = load_exercises()
    muscle_groups = ['Chest','Shoulder','Triceps','Back','Biceps','Legs']
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

if __name__=="__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
