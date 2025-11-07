import sys
import os
sys.path.append('src')

from strava_api import StravaAPI
from database import WorkoutDatabase 
from config.settings import DATABASE_PATH
from models.workout import Workout
from models.coach import Coach


def main():
    # Initialize Strava API connection and database 
    strava_api = StravaAPI()
    db = WorkoutDatabase(DATABASE_PATH)
    print("Database and strava API connection created")

    # Fetch activities from strava API
    activities = strava_api.get_recent_activities(num_activities=10)
    if not activities: 
        print("No activities found") 
        return
    print(f"Adding {len(activities)} fetched with success to the database")

    # Add activities to the DB
    for workout_data in activities:
        workout = Workout.from_strava(workout_data)  # create instance of workout class from the parsed data
        db.add_workout(workout)  # add workout to db
    print("All workouts added to the database")

    ###### DISPLAY CONTENT OF DB ######
    print("Your past workouts analyzed by coach: ")
    database_workout_content = db.get_all()
    for w in database_workout_content:
        print(f"name: {w.name}, type: {w.type}, distance: {w.distance}")

    ###### init the AI coach and ask for first question ######
    user_request = str(input("What do you want to ask coach ?"))
    coach = Coach(database_workout_content, behaviour="Encouraging and soft")
    print(coach.respond(user_request))


if __name__ == "__main__": 
    main()

