import random
from flask import Flask, render_template
import json

app = Flask(__name__)

# Function to read exercises from the JSON file
def read_exercises():
    with open('exercises.json', 'r') as f:
        exercises = json.load(f)
    return exercises

# Function to generate weekly workout plan
def generate_workout_plan():
    exercises = read_exercises()

    # Define the fixed exercises for each workout type
    workout_A_fixed = [
        {"name": "Smith Machine Incline Bench Press", "topic": "chest"},
        {"name": "Shoulder Press", "topic": "shoulder"},
        {"name": "Cable tricep pushdown", "topic": "triceps"}
    ]
    workout_B_fixed = [
        {"name": "Smith machine Rows", "topic": "back"},
        {"name": "Pully", "topic": "back"},
        {"name": "Cable Curl", "topic": "biceps"}
    ]
    workout_C_fixed = [
        {"name": "Smith Machine Squat", "topic": "legs"},
        {"name": "Leg extention", "topic": "legs"},
        {"name": "Calf Raises", "topic": "legs"}
    ]

    # Helper to select additional exercises by topic
    def select_additional_exercises(target_counts, fixed_exercises):
        additional = []
        for topic, count in target_counts.items():
            filtered = [
                e for e in exercises
                if e['topic'] == topic and e['name'] not in [fx['name'] for fx in fixed_exercises]
            ]
            additional.extend(random.sample(filtered, min(count, len(filtered))))
        return additional

    # Define target counts for additional exercises
    workout_A_targets = {"chest": 3 - 1, "shoulder": 2 - 1, "triceps": 2 - 1}
    workout_B_targets = {"back": 4 - 2, "biceps": 3 - 1}
    workout_C_targets = {"legs": 5 - 3}

    # Generate the workouts
    workout_A_plan = workout_A_fixed + select_additional_exercises(workout_A_targets, workout_A_fixed)
    workout_B_plan = workout_B_fixed + select_additional_exercises(workout_B_targets, workout_B_fixed)
    workout_C_plan = workout_C_fixed + select_additional_exercises(workout_C_targets, workout_C_fixed)

    # Sort exercises by topic
    def sort_workout_by_topic(workout):
        topics_order = ["chest", "shoulder", "triceps", "back", "biceps", "legs"]
        return sorted(workout, key=lambda x: topics_order.index(x['topic']))

    # Add 3–4 sets for each exercise
    def add_sets(workout):
        return [f"{exercise['name']} - {random.randint(3, 4)} sets" for exercise in sort_workout_by_topic(workout)]

    # Create the weekly plan
    weekly_plan = {
        'Monday': add_sets(workout_A_plan),
        'Tuesday': add_sets(workout_B_plan),
        'Wednesday': add_sets(workout_C_plan),
        'Friday': add_sets(workout_A_plan),
        'Saturday': add_sets(workout_B_plan),
        'Sunday': add_sets(workout_C_plan)
    }

    return weekly_plan

@app.route('/')
def index():
    weekly_plan = generate_workout_plan()  # Generate the workout plan
    return render_template('index.html', weekly_plan=weekly_plan)

if __name__ == '__main__':
    app.run(debug=True)
