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