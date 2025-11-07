from flask import Flask, render_template, jsonify, request, session
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import WorkoutDatabase
from config.settings import DATABASE_PATH
from config.personas import COACH_PERSONALITIES
from src.models.coach import Coach 

app = Flask(__name__)
app.secret_key = 'Antoine'

# Set Renato Canova as default coach
DEFAULT_COACH = 'canova'

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
                'elapsed_time': f"{round(workout.elapsed_time//60)}m{round(workout.elapsed_time%60)}s" if workout.elapsed_time else "0m0s",
                'moving_time': f"{round(workout.moving_time//60)}m{round(workout.moving_time%60)}s" if workout.moving_time else "0m0s",
                'total_elevation_gain': workout.total_elevation_gain or 0,
                'average_speed': round(workout.average_speed*3.6, 2) if workout.average_speed else 0,
                'max_speed': round(workout.max_speed*3.6, 2) if workout.max_speed else 0,
                'average_heartrate': round(workout.average_heartrate) if workout.average_heartrate else 0,
                'max_heartrate': round(workout.max_heartrate) if workout.max_heartrate else 0
            })
        return jsonify(workouts_data)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)})
    
@app.route('/coaches')
def coach_choice():
    return render_template('coaches.html')

@app.route('/api/select-coach', methods=['POST'])
def select_coach():
    """Store the selected coach in the current session"""
    data = request.get_json()
    coach_persona = data.get('coach_persona')  # Keep this as is
    
    if coach_persona in COACH_PERSONALITIES:
        session['selected_coach'] = coach_persona
        return jsonify({
            "success": True, 
            "coach_name": COACH_PERSONALITIES[coach_persona]['name']
        })
    else:
        return jsonify({
            "success": False, 
            "error": f"Invalid coach selection: {coach_persona}"
        })

@app.route('/api/get-selected-coach')
def get_selected_coach():
    """Get the currently selected coach"""
    selected_coach = session.get('selected_coach', DEFAULT_COACH)  
    coach_info = COACH_PERSONALITIES.get(selected_coach, COACH_PERSONALITIES[DEFAULT_COACH])
    return jsonify({
        "coach_type": selected_coach,
        "coach_name": coach_info['name']
    })

@app.route('/api/coach', methods=['POST'])
def ask_coach():
    try:
        data = request.get_json()
        user_question = data.get('question', '')

        # Get selected coach for current session, default to Renato Canova
        selected_coach_persona = session.get('selected_coach', DEFAULT_COACH)
        coach_personality = COACH_PERSONALITIES.get(selected_coach_persona)

        # If coach not found, use default (Renato)
        if coach_personality is None:
            selected_coach_persona = DEFAULT_COACH
            coach_personality = COACH_PERSONALITIES[DEFAULT_COACH]

        # Get workouts from database for context 
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'workouts.db')
        db = WorkoutDatabase(db_path)
        workouts = db.get_formatted_summary()[:10]
        

        # Create coach & answer question
        coach = Coach(past_workouts=workouts,
                      persona=coach_personality['behaviour'])
        response = coach.respond(user_question)
        
        return jsonify({
            "response": response,
            "coach_name": coach_personality['name']
        })
        
    except Exception as e:
        print(f"Error in ask_coach: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)