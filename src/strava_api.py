import requests
import sys
import os
from datetime import datetime
from src.models.workout import Workout 
from src.database import WorkoutDatabase
from config.settings import STRAVA_ACCESS_TOKEN, STRAVA_ACTIVITIES_URL
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class StravaAPI: 
    def __init__(self, access_token=STRAVA_ACCESS_TOKEN):
        self.access_token = access_token
        self.headers = {'Authorization': f'Bearer {access_token}'}

    def get_activities(self, per_page=30, page=1):
        """Fetch activities from Strava API"""
        params = {'per_page': per_page, 'page': page}
        response = requests.get(STRAVA_ACTIVITIES_URL,
                                headers=self.headers,
                                params=params)
        response.raise_for_status()
        return response.json()

    def get_recent_activities(self, num_activities=10):
        """Return the 10 most recent activities"""
        return self.get_activities(per_page=num_activities, page=1)
    
    def sync_to_database(self, db_path='workouts.db', num_activities=50):
        """
        Sync activities from Strava to database
        Returns: Number of new workouts added
        """
        try:
            # Initialize database
            db = WorkoutDatabase(db_path)
            
            # Get recent activities from Strava
            strava_activities = self.get_recent_activities(num_activities)
            
            # Get existing workout IDs to avoid duplicates
            existing_workouts = db.get_all()
            existing_ids = {workout.id for workout in existing_workouts}
            
            new_workouts_count = 0
            
            # Process each activity
            for activity in strava_activities:
                activity_id = activity.get('id')
                
                # Skip if already exists
                if activity_id in existing_ids:
                    continue
                
                # Convert to Workout object
                workout = self._create_workout_from_activity(activity)
                
                # Add to database
                db.add_workout(workout)
                new_workouts_count += 1
                
            print(f"Sync complete: {new_workouts_count} new workouts added")
            return new_workouts_count
            
        except Exception as e:
            print(f"Sync error: {e}")
            raise e
        
    def _create_workout_from_activity(self, activity):
        """Convert Strava activity JSON to Workout object"""
        
        # Parse start date
        start_date_str = activity.get('start_date', '')
        try:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        except:
            start_date = datetime.now()
        
        # Create Workout object
        workout = Workout(
            id=activity.get('id'),
            name=activity.get('name', 'Untitled'),
            type=activity.get('type', 'Unknown'),
            start_date=start_date,
            distance=activity.get('distance', 0),
            moving_time=activity.get('moving_time', 0),
            elapsed_time=activity.get('elapsed_time', 0),
            total_elevation_gain=activity.get('total_elevation_gain', 0),
            average_speed=activity.get('average_speed', 0),
            max_speed=activity.get('max_speed', 0),
            average_heartrate=activity.get('average_heartrate', 0),
            max_heartrate=activity.get('max_heartrate', 0)
        )
        
        return workout