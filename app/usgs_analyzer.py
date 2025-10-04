import requests
from typing import List, Dict
import time

class USGSAnalyzer:
    """USGS Earthquake Data Analyzer"""
    
    def __init__(self):
        self.base_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    
    def get_earthquakes_near_location(self, lat: float, lng: float, radius_km: float = 500) -> List[Dict]:
        """Get earthquakes near a specific location"""
        params = {
            'format': 'geojson',
            'latitude': lat,
            'longitude': lng,
            'maxradiuskm': radius_km,
            'starttime': '2020-01-01',
            'endtime': '2025-12-31',
            'minmagnitude': 4.0,
            'orderby': 'time'
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            earthquakes = []
            for feature in data.get('features', [])[:20]:
                props = feature['properties']
                coords = feature['geometry']['coordinates']
                
                earthquakes.append({
                    'magnitude': props['mag'],
                    'place': props['place'],
                    'time': props['time'],
                    'latitude': coords[1],
                    'longitude': coords[0],
                    'depth_km': coords[2],
                    'tsunami_warning': props.get('tsunami', 0),
                    'significance': props.get('sig', 0)
                })
            
            return earthquakes
        except Exception as e:
            print(f"Error fetching USGS data: {e}")
            return []
    
    def calculate_seismic_risk(self, lat: float, lng: float) -> Dict:
        """Calculate seismic risk for a location"""
        earthquakes = self.get_earthquakes_near_location(lat, lng, 300)
        
        if not earthquakes:
            return {
                "risk_level": "low",
                "earthquakes_count": 0,
                "max_magnitude": 0,
                "confidence": "high",
                "message": "Seismically stable area"
            }
        
        magnitudes = [q['magnitude'] for q in earthquakes]
        max_mag = max(magnitudes)
        avg_mag = sum(magnitudes) / len(magnitudes)
        
        three_years_ago = time.time() * 1000 - (3 * 365 * 24 * 60 * 60 * 1000)
        recent_quakes = len([q for q in earthquakes if q['time'] > three_years_ago])
        
        if max_mag > 7.0 or recent_quakes > 15:
            risk_level = "very_high"
        elif max_mag > 6.5 or recent_quakes > 8:
            risk_level = "high" 
        elif max_mag > 5.5 or recent_quakes > 3:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "risk_level": risk_level,
            "earthquakes_count": len(earthquakes),
            "max_magnitude": max_mag,
            "average_magnitude": round(avg_mag, 1),
            "recent_activity": recent_quakes,
            "seismic_hazard": self.get_hazard_description(risk_level),
            "recommendation": self.get_seismic_recommendation(risk_level)
        }
    
    def get_hazard_description(self, risk_level: str) -> str:
        descriptions = {
            "very_high": "Active fault zone - history of destructive earthquakes",
            "high": "Frequent seismic activity - potential for strong earthquakes", 
            "medium": "Moderate seismic activity - potential for medium tremors",
            "low": "Stable area - rare seismic activity"
        }
        return descriptions.get(risk_level, "Unknown")
    
    def get_seismic_recommendation(self, risk_level: str) -> str:
        recommendations = {
            "very_high": "🚨 Avoid construction - emergency evacuation plans - reinforce all buildings",
            "high": "⚠️ Earthquake-resistant construction - early warning systems - emergency training",
            "medium": "🔍 Monitor activity - risk assessment - preventive measures",
            "low": "✅ Standard preventive measures - routine monitoring"
        }
        return recommendations.get(risk_level, "Needs additional assessment")