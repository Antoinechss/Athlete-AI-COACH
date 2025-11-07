from flask import Flask, render_template, jsonify, request
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import WorkoutDatabase
from config.settings import DATABASE_PATH
from src.models.coach import Coach 

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/workouts')
def get_workouts():
    try:
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'workouts.db')
        db = WorkoutDatabase(db_path)
        workouts = db.get_all()
        
        workouts_data = []
        for workout in workouts:
            workouts_data.append({
                'start_date': workout.start_date,
                'name': workout.name,
                'type': workout.type,
                'distance': round(workout.distance/1000, 1) if workout.distance else 0,
                'elapsed_time': workout.elapsed_time,
                'moving_time': workout.moving_time,
                'total_elevation_gain': workout.total_elevation_gain,
                'average_speed': workout.average_speed,
                'max_speed': workout.max_speed,
                'average_heartrate': workout.average_heartrate,
                'max_heartrate': workout.max_heartrate
            })
        return jsonify(workouts_data)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)})

@app.route('/api/coach', methods=['POST'])
def ask_coach():
    data = request.get_json()
    user_question = data.get('question','')

    # get workouts from database for context 
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'workouts.db')
    db = WorkoutDatabase(db_path)
    workouts = db.get_all()

    # Create coach & answer question 
    coach = Coach(past_workouts=workouts, 
                  behaviour='encouraging and analytical')
    response = coach.respond(user_question)
    return jsonify({"response": response})


if __name__ == '__main__':
    app.run(debug=True)
