# Database layer with sqlite

import sqlite3
from typing import List, Optional
from datetime import datetime
from src.models.workout import Workout

class WorkoutDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """ Create the blank workouts table """
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workouts(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL, 
                start_date DATETIME NOT NULL, 
                distance REAL,
                moving_time REAL, 
                elapsed_time REAL,
                total_elevation_gain REAL,
                average_speed REAL,
                max_speed REAL,
                average_heartrate REAL,
                max_heartrate REAL)
            """)
        
        connection.commit()
        connection.close()

    def add_workout(self, workout: Workout):
        """ add the stats of a workout to the database """
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO workouts 
            (id, name, type, start_date, distance, moving_time, 
            elapsed_time, total_elevation_gain, average_speed, 
            max_speed, average_heartrate, max_heartrate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """,
            (workout.id,
             workout.name,
             workout.type,
             workout.start_date,
             workout.distance,
             workout.moving_time,
             workout.elapsed_time,
             workout.total_elevation_gain,
             workout.average_speed,
             workout.max_speed,
             workout.average_heartrate,
             workout.max_heartrate))
        
        connection.commit()
        connection.close()
  
    def get_all(self):
        """Fetch all workouts from DB"""
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute("""SELECT * FROM workouts ORDER BY start_date DESC""")
        workouts_data = cursor.fetchall()

        workouts = []
        for w in workouts_data:
            # Convert string back to datetime object
            try:
                if isinstance(w[3], str):
                    start_date = datetime.fromisoformat(w[3].replace('Z', '+00:00'))
                else:
                    start_date = w[3]
            except (ValueError, AttributeError):
                start_date = datetime.now()  # Fallback

            act = Workout(
                id=w[0],
                name=w[1],
                type=w[2],
                start_date=w[3],
                distance=w[4],
                moving_time=w[5],
                elapsed_time=w[6],
                total_elevation_gain=w[7],
                average_speed=w[8],
                max_speed=w[9],
                average_heartrate=w[10],
                max_heartrate=w[11])
            workouts.append(act)

        connection.close()
        return workouts
    
    def get_formatted_summary(self):
        """Format the data from the workouts before coach's analysis"""
        workouts = self.get_all()
        formatted_workouts = []

        for workout in workouts : 
            # Dealing with elapsed time 
            elapsed_minutes = workout.elapsed_time // 60 if workout.elapsed_time else 0
            elapsed_hours = elapsed_minutes // 60
            elapsed_mins_remaining = elapsed_minutes % 60
            
            if elapsed_hours > 0:
                time_str = f"{elapsed_hours}h {elapsed_mins_remaining}m"
            else:
                time_str = f"{elapsed_mins_remaining}m"

            # Distance --> convert to kms 
            distance_km = round(workout.distance / 1000, 2) if workout.distance else 0

            # Pace (min/km)
            if workout.distance and workout.moving_time:
                pace_seconds_per_km = (workout.moving_time / (workout.distance / 1000))
                pace_minutes = int(pace_seconds_per_km // 60)
                pace_seconds = int(pace_seconds_per_km % 60)
                pace_str = f"{pace_minutes}:{pace_seconds:02d}/km"
            else:
                pace_str = "unknown pace"

            # Date - safely handle both datetime objects and strings
            try:
                if hasattr(workout.start_date, 'strftime'):
                    date_str = workout.start_date.strftime('%Y-%m-%d')
                elif isinstance(workout.start_date, str):
                    # Try to parse the string and format it
                    dt = datetime.fromisoformat(workout.start_date.replace('Z', '+00:00'))
                    date_str = dt.strftime('%Y-%m-%d')
                else:
                    date_str = str(workout.start_date)[:10]  # Take first 10 chars (YYYY-MM-DD)
            except (ValueError, AttributeError):
                date_str = "unknown date"

            # Build summary
            workout_summary = f"{date_str} - {workout.name}: {workout.type}, {distance_km}km in {time_str}, pace {pace_str}"
            
            # Add heart rate if available
            if workout.average_heartrate:
                workout_summary += f", avg HR {int(workout.average_heartrate)}bpm"
            
            # Add elevation if significant
            if workout.total_elevation_gain and workout.total_elevation_gain > 20:
                workout_summary += f", elevation gain {int(workout.total_elevation_gain)}m"
            
            formatted_workouts.append(workout_summary)
        
        return formatted_workouts



    
