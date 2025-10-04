import requests
import time
import random
from typing import Dict, Tuple

class LocationAnalyzer:
    """محلل المناطق وتقدير الوفيات"""
    
    def __init__(self):
        self.user_agent = 'AsteroidDefenderApp/1.0'
    
    def is_ocean_location(self, lat: float, lng: float) -> bool:
        """كشف المحيطات باستخدام الخرائط الجغرافية"""
        # المحيط الهادئ
        if (-60 <= lat <= 60) and (-180 <= lng <= -60):
            return True
        # المحيط الأطلسي
        if (-60 <= lat <= 60) and (-60 <= lng <= 20):
            return True
        # المحيط الهندي
        if (-60 <= lat <= 30) and (20 <= lng <= 120):
            return True
        return False
    
    def get_location_type(self, lat: float, lng: float) -> str:
        """تحديد نوع المنطقة من الإحداثيات"""
        try:
            if self.is_ocean_location(lat, lng):
                return "ocean"
            
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {'lat': lat, 'lon': lng, 'format': 'json'}
            headers = {'User-Agent': self.user_agent}
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                address = data.get('address', {})
                
                if 'city' in address or 'town' in address:
                    return "urban_high"
                elif 'village' in address or 'suburb' in address:
                    return "urban_medium"
                elif 'country' in address:
                    return "rural"
                else:
                    return "unknown"
            else:
                return "unknown"
                
        except Exception:
            return "unknown"
    
    def estimate_death_toll(self, asteroid_energy: float, location_type: str, impact_radius_km: float) -> Dict:
        """تقدير عدد الوفيات المتوقع من اصطدام كويكب بناءً على الطاقة، نوع الموقع، ونصف قطر التأثير."""

        casualty_factors = {
            "ocean": 0.001,
            "rural": 0.01,
            "urban_medium": 0.1,
            "urban_high": 0.5,
            "unknown": 0.05
        }

        affected_area = 3.14159 * (impact_radius_km ** 2)

        population_density = {
            "ocean": 0,
            "rural": 30,
            "urban_medium": 1000,
            "urban_high": 10000,
            "unknown": 100
        }

        base_population = affected_area * population_density.get(location_type, 100)
        casualty_factor = casualty_factors.get(location_type, 0.05)
        estimated_deaths = int(base_population * casualty_factor)

        if location_type == "ocean" and asteroid_energy > 10:
            estimated_deaths += int(asteroid_energy * 10000)

        return {
            "estimated_deaths": estimated_deaths,
            "affected_area_km2": affected_area,
            "estimated_population": int(base_population),
            "casualty_rate": f"{casualty_factor * 100}%"
        }

    def generate_impact_site(self, asteroid_id: int) -> Tuple[float, float]:
        """توليد إحداثيات موقع الاصطدام اعتماداً على رقم الكويكب (Deterministic)."""
        random.seed(asteroid_id)
        lat = random.uniform(-60, 60)
        lng = random.uniform(-180, 180)
        return lat, lng

    def calculate_impact_radius(self, energy_megatons: float) -> float:
        """حساب نصف قطر التأثير التقريبي (كم) بناءً على الطاقة."""
        # معادلة تقريبية: كل 1 ميغاطن TNT ≈ 1 كم نصف قطر
        return max(1, energy_megatons ** 0.5 * 2)

    def get_location_description(self, location_type: str) -> str:
        """وصف الموقع"""
        descriptions = {
            "ocean": "محيط - خطر تسونامي محتمل",
            "rural": "منطقة ريفية - كثافة سكانية منخفضة", 
            "urban_medium": "منطقة حضرية متوسطة - كثافة سكانية عالية",
            "urban_high": "منطقة حضرية عالية الكثافة - خطر كبير",
            "unknown": "منطقة غير معروفة - افتراض خطر متوسط"
        }
        return descriptions.get(location_type, "منطقة غير معروفة")

    def get_primary_threat(self, location_type: str) -> str:
        """تحديد التهديد الرئيسي"""
        threats = {
            "ocean": "🌊 تسونامي وأمواج صدمية",
            "rural": "💥 انفجار وموجة صدمية",
            "urban_medium": "💥 دمار مباشر وحرائق", 
            "urban_high": "💥 دمار شامل وحرائق واسعة",
            "unknown": "⚠️ تأثير مباشر"
        }
        return threats.get(location_type, "⚠️ تأثير غير محدد")

    def analyze_impact(self, asteroid_data: Dict, impact_lat: float, impact_lng: float) -> Dict:
        """تحليل تأثير كويكب على موقع محدد"""
        location_type = self.get_location_type(impact_lat, impact_lng)
        impact_radius = self.calculate_impact_radius(asteroid_data["energy_megatons_TNT"])
        
        results = self.estimate_death_toll(
            asteroid_energy=asteroid_data["energy_megatons_TNT"],
            location_type=location_type,
            impact_radius_km=impact_radius
        )
        
        return {
            "asteroid_name": asteroid_data["name"],
            "impact_location": {
                "coordinates": [impact_lat, impact_lng],
                "type": location_type,
                "description": self.get_location_description(location_type)
            },
            "impact_analysis": {
                "energy_megatons": asteroid_data["energy_megatons_TNT"],
                "impact_radius_km": impact_radius,
                "estimated_deaths": results["estimated_deaths"],
                "affected_area_km2": results["affected_area_km2"],
                "estimated_population": results["estimated_population"],
                "casualty_rate": results["casualty_rate"],
                "primary_threat": self.get_primary_threat(location_type)
            }
        }

# إنشاء instance عام
location_analyzer = LocationAnalyzer()
