import os
from dotenv import load_dotenv

load_dotenv()

# Strava API configuration
STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
STRAVA_ACCESS_TOKEN = os.getenv('STRAVA_ACCESS_TOKEN')

# Database configuration
DATABASE_PATH = 'workouts.db'

# API endpoints
STRAVA_ACTIVITIES_URL = 'https://www.strava.com/api/v3/activities'

