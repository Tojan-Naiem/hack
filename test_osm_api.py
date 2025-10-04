# جرب هذا الكود للتأكد
import requests
import requests

def get_location_type(lat, lng):
    # استدعاء OpenStreetMap Nominatim API
    url = f"https://nominatim.openstreetmap.org/reverse"
    params = {
        'lat': lat,
        'lon': lng,
        'format': 'json'
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    # استخراج نوع المنطقة
    if 'water' in data.get('type', '') or 'sea' in data.get('type', ''):
        return "ocean"
    elif 'city' in data.get('type', '') or 'town' in data.get('type', ''):
        return "urban_high"
    elif 'village' in data.get('type', '') or 'suburb' in data.get('type', ''):
        return "urban_medium"
    else:
        return "rural"
    
def test_osm_api():
    # إحداثيات تجريبية (روما مثالاً)
    test_coords = [
        (41.9028, 12.4964),  # روما - مدينة
        (48.8566, 2.3522),   # باريس - مدينة  
        (-45.0, -170.0),     # المحيط الهادئ
        (25.0, 55.0),        # دبي - صحراء
    ]
    
    for lat, lng in test_coords:
        location_type = get_location_type(lat, lng)
        print(f"📍 ({lat}, {lng}) → {location_type}")

# شغل الاختبار
test_osm_api()