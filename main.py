import sys
from strava_api import StravaAPI
from database import WorkoutDatabase 
from config.settings import DATABASE_PATH
from models.workout import Workout
sys.path.append('src')


def sync_workouts():
    # Initialize Strava API connection and database 
    strava_api = StravaAPI()
    db = WorkoutDatabase(DATABASE_PATH)

    # Fetch activities from strava API
    activities = strava_api.get_recent_activities(num_activities=10)
    if not activities:
        return
 
    # Add fetched activities to the DB
    for workout_data in activities:
        workout = Workout.from_strava(workout_data)  # create instance of workout class from the parsed data
        db.add_workout(workout)  # add workout to db


if __name__ == "__main__": 
    sync_workouts()

