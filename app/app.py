from flask import Flask, render_template, jsonify
import sys
import os
sys.path.append('src')

from src.database import WorkoutDatabase
from config.settings import DATABASE_PATH

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/workouts')
def get_workouts():
    workouts = WorkoutDatabase(DATABASE_PATH).get_all()
    workouts_data = {}
    for workout in workouts:
        workouts_data.append({
            'id': workout.id,
            'name': workout.name,
            'type': workout.type,
            'start_date': workout.start_date,
            'distance': workout.distance,
            'moving_time': workout.moving_time,
            'elapsed_time': workout.elapsed_time,
            'total_elevation_gain': workout.total_elevation_gain,
            'average_speed': workout.average_speed,
            'max_speed': workout.max_speed,
            'average_heartrate': workout.average_heartrate,
            'max_heartrate': workout.max_heartrate
        })
    return jsonify(workouts_data)


if __name__ == '__main__':
    app.run(debug=True)
