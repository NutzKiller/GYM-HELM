# app/workout.py
import random
from flask import flash
from app.helpers import load_exercises

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

def generate_full_body_plan(ex):
    def single():
        w = []
        # Chest: Smith Machine Incline Bench Press + one random chest exercise
        chest_main = get_exercise_by_name(ex, "Smith Machine Incline Bench Press")
        if chest_main:
            w.append(chest_main)
            chest_pool = [c for c in ex if c['topic'].lower() == 'chest' and c['name'] != chest_main['name']]
            if chest_pool:
                w.append(random.choice(chest_pool))
        # Back: one of (Pull Ups, Lats Pulldown) and one of (Smith machine Rows, T-Bar row)
        b1 = pick_one_from_pair(ex, "Pull Ups", "Lats Pulldown")
        b2 = pick_one_from_pair(ex, "Smith machine Rows", "T-Bar row")
        if b1:
            w.append(b1)
        if b2:
            w.append(b2)
        # Legs: one of (Calf Raises, Sitting Calf Raises) and either Smith Machine Squat or Hack Squat
        l1 = pick_one_from_pair(ex, "Calf Raises", "Sitting Calf Raises")
        if l1:
            w.append(l1)
        # Modified: choose between "Smith Machine Squat" or "Hack Squat"
        sq = pick_one_from_pair(ex, "Smith Machine Squat", "Hack Squat")
        if sq:
            w.append(sq)
        # Shoulders: one of (Sitting Lateral raise, Cable Lateral raise) and Shoulder Press
        s1 = pick_one_from_pair(ex, "Sitting Lateral raise", "Cable Lateral raise")
        sp = get_exercise_by_name(ex, "Shoulder Press")
        if s1:
            w.append(s1)
        if sp:
            w.append(sp)
        # Biceps: Cable Curl
        bc = get_exercise_by_name(ex, "Cable Curl")
        if bc:
            w.append(bc)
        # Triceps: Cable tricep pushdown
        tri = get_exercise_by_name(ex, "Cable tricep pushdown")
        if tri:
            w.append(tri)
        return [f"{x['name']} - 3 sets" for x in w if x]
    return {
        "Monday": single(),
        "Wednesday": single(),
        "Friday": single()
    }

def generate_ab_plan(ex):
    def workout_A():
        w = []
        # Chest
        cm = get_exercise_by_name(ex, "Smith Machine Incline Bench Press")
        if cm:
            w.append(f"{cm['name']} - 3 sets")
        chest_pool = [c for c in ex if c['topic'].lower() == 'chest' and (cm is None or c['name'] != cm['name'])]
        if len(chest_pool) >= 2:
            for c in random.sample(chest_pool, 2):
                w.append(f"{c['name']} - 3 sets")
        # Shoulders
        shoulder_pair = pick_one_from_pair(ex, "Dumbbell Lateral raise", "Sitting Lateral raise")
        if shoulder_pair:
            w.append(f"{shoulder_pair['name']} - 4 sets")
            shoulder_pool = [s for s in ex if s['topic'].lower() == 'shoulders' and s['name'] != shoulder_pair['name']]
            if shoulder_pool:
                w.append(f"{random.choice(shoulder_pool)['name']} - 3 sets")
        # Triceps
        tricep_pool = [t for t in ex if t['topic'].lower() == 'triceps']
        if len(tricep_pool) >= 2:
            tricep_main, tricep_secondary = random.sample(tricep_pool, 2)
            w.append(f"{tricep_main['name']} - 4 sets")
            w.append(f"{tricep_secondary['name']} - 3 sets")
        return w

    def workout_B():
        w = []
        # Back
        back_pair1 = pick_one_from_pair(ex, "Pull Ups", "Lats Pulldown")
        back_pair2 = pick_one_from_pair(ex, "Smith machine Rows", "T-Bar row")
        if back_pair1:
            w.append(f"{back_pair1['name']} - 3 sets")
        if back_pair2:
            w.append(f"{back_pair2['name']} - 3 sets")
        back_pool = [bk for bk in ex if bk['topic'].lower() == 'back' and (back_pair1 is None or bk['name'] != back_pair1['name']) and (back_pair2 is None or bk['name'] != back_pair2['name'])]
        if back_pool:
            w.append(f"{random.choice(back_pool)['name']} - 3 sets")
        # Legs: Modified to use either Smith Machine Squat or Hack Squat
        sq = pick_one_from_pair(ex, "Smith Machine Squat", "Hack Squat")
        if sq:
            w.append(f"{sq['name']} - 4 sets")
        calf_pair = pick_one_from_pair(ex, "Calf Raises", "Sitting Calf Raises")
        if calf_pair:
            w.append(f"{calf_pair['name']} - 3 sets")
        legs_pool = [lg for lg in ex if lg['topic'].lower() == 'legs' and (sq is None or lg['name'] != sq['name']) and (calf_pair is None or lg['name'] != calf_pair['name'])]
        if legs_pool:
            w.append(f"{random.choice(legs_pool)['name']} - 3 sets")
        # Biceps
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

def generate_ppl_plan(ex):
    def push_day():
        w = []
        chest_main = get_exercise_by_name(ex, "Smith Machine Incline Bench Press")
        if chest_main:
            w.append({"name": chest_main['name'], "sets": 4})
            chest_secondary = pick_one_from_pair(ex, "Cable Crossover", "Machine Pec Fly")
            if chest_secondary:
                w.append({"name": chest_secondary['name'], "sets": 3})
            chest_pool = [c for c in ex if c['topic'].lower() == 'chest' and (chest_main is None or c['name'] not in [chest_main['name'], chest_secondary['name'] if chest_secondary else ""])]
            if chest_pool:
                w.append({"name": random.choice(chest_pool)['name'], "sets": 3})
        shoulder_main = get_exercise_by_name(ex, "Shoulder Press")
        if shoulder_main:
            w.append({"name": shoulder_main['name'], "sets": 4})
            shoulder_secondary = pick_one_from_pair(ex, "Sitting Lateral raise", "Cable Lateral raise")
            if shoulder_secondary:
                w.append({"name": shoulder_secondary['name'], "sets": 3})
        tricep_main = get_exercise_by_name(ex, "Cable tricep pushdown")
        if tricep_main:
            w.append({"name": tricep_main['name'], "sets": 4})
            tricep_pool = [t for t in ex if t['topic'].lower() == 'triceps' and t['name'] != tricep_main['name']]
            if tricep_pool:
                w.append({"name": random.choice(tricep_pool)['name'], "sets": 4})
        return [f"{item['name']} - {item['sets']} sets" for item in w]

    def pull_day():
        w = []
        back_main = get_exercise_by_name(ex, "Smith machine Rows")
        if back_main:
            w.append({"name": back_main['name'], "sets": 3})
        back_option = pick_one_from_pair(ex, "Pull Ups", "Lats Pulldown")
        if back_option:
            w.append({"name": back_option['name'], "sets": 3})
        back_pool = [b for b in ex if b['topic'].lower() == 'back' and (back_main is None or b['name'] != back_main['name']) and (back_option is None or b['name'] != back_option['name'])]
        for _ in range(2):
            if back_pool:
                additional_back = random.choice(back_pool)
                w.append({"name": additional_back['name'], "sets": 3})
                back_pool.remove(additional_back)
        bicep_main = get_exercise_by_name(ex, "Cable Curl")
        if bicep_main:
            w.append({"name": bicep_main['name'], "sets": 3})
            bicep_pool = [b for b in ex if b['topic'].lower() == 'biceps' and b['name'] != bicep_main['name']]
            for _ in range(2):
                if bicep_pool:
                    additional_bicep = random.choice(bicep_pool)
                    w.append({"name": additional_bicep['name'], "sets": 3})
                    bicep_pool.remove(additional_bicep)
        return [f"{item['name']} - {item['sets']} sets" for item in w]

    def legs_day():
        w = []
        # Modified: Instead of fixed "Smith Machine Squat", choose between "Smith Machine Squat" and "Hack Squat"
        squat = pick_one_from_pair(ex, "Smith Machine Squat", "Hack Squat")
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
        leg_pool = [lg for lg in ex if lg['topic'].lower() == 'legs' and (squat is None or lg['name'] != squat['name']) and (leg_extension is None or lg['name'] != leg_extension['name']) and (calf is None or lg['name'] != calf['name']) and (leg_curl is None or lg['name'] != leg_curl['name'])]
        for _ in range(1):
            if leg_pool and len(w) < 6:
                additional_leg = random.choice(leg_pool)
                w.append({"name": additional_leg['name'], "sets": 3})
                leg_pool.remove(additional_leg)
        total_sets = sum(item['sets'] for item in w)
        if total_sets > 17 and w:
            excess = total_sets - 17
            if w[-1]['sets'] > 3:
                w[-1]['sets'] -= excess
                if w[-1]['sets'] < 3:
                    w[-1]['sets'] = 3
        return [f"{item['name']} - {item['sets']} sets" for item in w]

    return {
        "Monday": push_day(),
        "Tuesday": pull_day(),
        "Wednesday": legs_day(),
        "Friday": push_day(),
        "Saturday": pull_day(),
        "Sunday": legs_day()
    }

def generate_new_abc_plan(ex):
    def workout_A():
        w = []
        chest_main = get_exercise_by_name(ex, "Smith Machine Incline Bench Press")
        if chest_main:
            w.append({"name": chest_main['name'], "sets": 3})
            chest_secondary = pick_one_from_pair(ex, "Machine Pec Fly", "Cable Crossover")
            if chest_secondary:
                w.append({"name": chest_secondary['name'], "sets": 3})
            chest_pool = [c for c in ex if c['topic'].lower() == 'chest' and (chest_main is None or c['name'] not in [chest_main['name'], chest_secondary['name'] if chest_secondary else ""])]
            for _ in range(2):
                if chest_pool:
                    additional_chest = random.choice(chest_pool)
                    w.append({"name": additional_chest['name'], "sets": 3})
                    chest_pool.remove(additional_chest)
        back_main = get_exercise_by_name(ex, "Smith machine Rows")
        if back_main:
            w.append({"name": back_main['name'], "sets": 3})
            back_option = pick_one_from_pair(ex, "Pull Ups", "Lats Pulldown")
            if back_option:
                w.append({"name": back_option['name'], "sets": 3})
            back_pool = [b for b in ex if b['topic'].lower() == 'back' and (back_main is None or b['name'] != back_main['name']) and (back_option is None or b['name'] != back_option['name'])]
            for _ in range(2):
                if back_pool:
                    additional_back = random.choice(back_pool)
                    w.append({"name": additional_back['name'], "sets": 3})
                    back_pool.remove(additional_back)
        return [f"{item['name']} - {item['sets']} sets" for item in w]

    def workout_B():
        w = []
        shoulder_main = get_exercise_by_name(ex, "Shoulder Press")
        if shoulder_main:
            w.append({"name": shoulder_main['name'], "sets": 3})
            shoulder_secondary = pick_one_from_pair(ex, "Sitting Lateral raise", "Cable Lateral raise")
            if shoulder_secondary:
                w.append({"name": shoulder_secondary['name'], "sets": 3})
            shoulder_pool = [s for s in ex if s['topic'].lower() == 'shoulder' and (shoulder_main is None or s['name'] not in [shoulder_main['name'], shoulder_secondary['name'] if shoulder_secondary else ""])]
            if shoulder_pool:
                w.append({"name": random.choice(shoulder_pool)['name'], "sets": 3})
        bicep_main = get_exercise_by_name(ex, "Cable Curl")
        if bicep_main:
            w.append({"name": bicep_main['name'], "sets": 3})
            bicep_pool = [b for b in ex if b['topic'].lower() == 'biceps' and b['name'] != bicep_main['name']]
            for _ in range(2):
                if bicep_pool:
                    additional_bicep = random.choice(bicep_pool)
                    w.append({"name": additional_bicep['name'], "sets": 3})
                    bicep_pool.remove(additional_bicep)
        tricep_main = get_exercise_by_name(ex, "Cable tricep pushdown")
        if tricep_main:
            w.append({"name": tricep_main['name'], "sets": 3})
            tricep_pool = [t for t in ex if t['topic'].lower() == 'triceps' and t['name'] != tricep_main['name']]
            for _ in range(2):
                if tricep_pool:
                    additional_tricep = random.choice(tricep_pool)
                    w.append({"name": additional_tricep['name'], "sets": 3})
                    tricep_pool.remove(additional_tricep)
        return [f"{item['name']} - {item['sets']} sets" for item in w]

    def workout_C():
        w = []
        # Modified: choose between "Smith Machine Squat" or "Hack Squat"
        squat = pick_one_from_pair(ex, "Smith Machine Squat", "Hack Squat")
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
        leg_pool = [lg for lg in ex if lg['topic'].lower() == 'legs' and (squat is None or lg['name'] not in [squat['name']]) and (leg_extension is None or lg['name'] not in [leg_extension['name']]) and (calf is None or lg['name'] != calf['name']) and (leg_curl is None or lg['name'] != leg_curl['name'])]
        for _ in range(2):
            if leg_pool and len(w) < 6:
                additional_leg = random.choice(leg_pool)
                w.append({"name": additional_leg['name'], "sets": 3})
                leg_pool.remove(additional_leg)
        return [f"{item['name']} - {item['sets']} sets" for item in w]

    return {
        "Monday": workout_A(),
        "Tuesday": workout_B(),
        "Wednesday": workout_C(),
        "Friday": workout_A(),
        "Saturday": workout_B(),
        "Sunday": workout_C()
    }

# NEW: Custom workout plan option
def generate_custom_plan(ex, num_days, chosen_exercises):
    """
    Generate a custom workout plan.
    
    Parameters:
      - ex: the list of exercises loaded from the library.
      - num_days: an integer, the number of days per week for the custom plan.
      - chosen_exercises: either a list of exercise names (to be used for every day) or a dictionary 
        mapping day numbers (or day identifiers) to lists of exercise names.
      
    Returns:
      A dictionary where keys are day names ("Day 1", "Day 2", etc.) and values are lists
      of strings describing each exercise with a default of 3 sets.
    """
    plan = {}
    # If chosen_exercises is a dict, allow different exercises per day.
    if isinstance(chosen_exercises, dict):
        for i in range(1, num_days + 1):
            day_key = f"Day {i}"
            workout_day = []
            # Try to get the list for this day from the dict (supports int or str keys)
            day_exercises = chosen_exercises.get(i) or chosen_exercises.get(str(i)) or []
            for ex_name in day_exercises:
                exercise = get_exercise_by_name(ex, ex_name)
                if exercise:
                    workout_day.append(f"{exercise['name']} - 3 sets")
            plan[day_key] = workout_day
    else:
        # Otherwise, assume chosen_exercises is a list to be used for every day.
        for i in range(1, num_days + 1):
            day_key = f"Day {i}"
            workout_day = []
            for ex_name in chosen_exercises:
                exercise = get_exercise_by_name(ex, ex_name)
                if exercise:
                    workout_day.append(f"{exercise['name']} - 3 sets")
            plan[day_key] = workout_day
    return plan

# Updated: generate_workout_plan now supports a 'custom' plan type.
def generate_workout_plan(plan_type, num_days=None, chosen_exercises=None):
    ex = load_exercises()
    if plan_type == 'full_body':
        return generate_full_body_plan(ex)
    elif plan_type == 'ab':
        return generate_ab_plan(ex)
    elif plan_type == 'ppl':
        return generate_ppl_plan(ex)
    elif plan_type == 'abc':
        return generate_new_abc_plan(ex)
    elif plan_type == 'custom':
        if num_days is None or chosen_exercises is None:
            flash("Custom plan requires number of days and a list (or dictionary) of chosen exercises.")
            return {}
        return generate_custom_plan(ex, num_days, chosen_exercises)
    else:
        return {}