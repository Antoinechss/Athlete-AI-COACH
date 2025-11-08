import requests
import sys
import os
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
    
  