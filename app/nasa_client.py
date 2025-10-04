import requests
from datetime import datetime, timedelta
from typing import List
from app.models import Asteroid
from app.config import Config

class NASAAPIClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or Config.NASA_API_KEY
        self.base_url = Config.NASA_BASE_URL
    
    def fetch_asteroids(self, start_date=None, end_date=None):
        """جلب البيانات من NASA"""
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if not end_date:
            end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        url = f"{self.base_url}/feed"
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'api_key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error fetching from NASA: {e}")
            return None
    
    def parse_nasa_data(self, raw_data) -> List[Asteroid]:
        """تحويل بيانات NASA"""
        asteroids = []
        
        if not raw_data or 'near_earth_objects' not in raw_data:
            return asteroids
        
        for date, objects in raw_data['near_earth_objects'].items():
            for obj in objects:
                asteroid = Asteroid(
                    id=int(obj['id']),
                    name=obj['name'],
                    date=date,
                    diameter_avg=obj['estimated_diameter']['meters']['estimated_diameter_max'],
                    velocity_km_s=float(obj['close_approach_data'][0]['relative_velocity']['kilometers_per_second']),
                    miss_distance_km=float(obj['close_approach_data'][0]['miss_distance']['kilometers']),
                    energy_megatons_TNT=0,
                    is_potentially_hazardous=obj['is_potentially_hazardous_asteroid']
                )
                asteroids.append(asteroid)
        
        return asteroids

