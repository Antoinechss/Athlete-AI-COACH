from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import sys
import os
from functools import wraps
from src.strava_api import StravaAPI
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import WorkoutDatabase
from config.settings import DATABASE_PATH
from config.personas import COACH_PERSONALITIES
from src.models.coach import Coach 

app = Flask(__name__)
app.secret_key = 'Antoine'

# Login 

def simple_check(username, password):
    """Credential check"""
    users = {
        'user1': 'user1password', 
        'user2': 'user2password',
        'user3': 'user3password',
    }
    return users.get(username) == password

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if simple_check(username, password):
            session['user_id'] = username
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Set Renato Canova as default coach
DEFAULT_COACH = 'canova'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
@login_required 
def dashboard():
    return render_template('index.html')

@app.route('/coaches')
@login_required 
def coach_choice():
    return render_template('coaches.html')

@app.route('/api/workouts')
@login_required 
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

@app.route('/api/select-coach', methods=['POST'])
def select_coach():
    """Store the selected coach in the current session"""
    data = request.get_json()
    coach_persona = data.get('coach_persona')
    
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
@login_required 
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
    
@app.route('/api/sync-strava', methods=['POST'])
@login_required
def sync_strava():
    """Sync workouts from Strava to database"""
    try:
        # Get database path
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'workouts.db')
        
        # Use your existing StravaAPI class
        strava_api = StravaAPI()
        new_workouts_count = strava_api.sync_to_database(db_path=db_path, num_activities=50)
        
        return jsonify({
            "success": True,
            "message": f"Successfully synced {new_workouts_count} new workouts",
            "new_workouts": new_workouts_count
        })
        
    except Exception as e:
        print(f"Strava sync error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)