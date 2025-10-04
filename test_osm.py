import requests
import time

def get_location_type(lat, lng):
    """
    تحديد نوع المنطقة من الإحداثيات باستخدام OpenStreetMap
    """
    try:
        # استدعاء OpenStreetMap API
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': lat,
            'lon': lng,
            'format': 'json'
        }
        
        # إضافة headers لتجنب حظر الطلبات
        headers = {
            'User-Agent': 'AsteroidDefenderApp/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # تحليل الاستجابة
            place_type = data.get('type', 'unknown')
            category = data.get('category', 'unknown')
            address = data.get('address', {})
            
            # تحديد نوع المنطقة
            if place_type in ['sea', 'ocean', 'bay'] or category == 'water':
                return "ocean"
            elif 'city' in address or 'town' in address:
                return "urban_high"
            elif 'village' in address or 'suburb' in address:
                return "urban_medium"
            elif 'country' in address:
                return "rural"
            else:
                return "unknown"
        else:
            return f"error_{response.status_code}"
            
    except Exception as e:
        return f"exception_{str(e)}"

def test_osm_api():
    """
    اختبار API على إحداثيات مختلفة
    """
    # إحداثيات تجريبية
    test_coords = [
        (41.9028, 12.4964),  # روما - مدينة
        (48.8566, 2.3522),   # باريس - مدينة  
        (-45.0, -170.0),     # المحيط الهادئ
        (25.0, 55.0),        # دبي - صحراء
        (35.6762, 139.6503), # طوكيو - مدينة
        (40.7128, -74.0060), # نيويورك - مدينة
        (0, 0),              # المحيط الأطلسي
    ]
    
    print("🚀 بدء اختبار OpenStreetMap API...")
    print("=" * 50)
    
    for i, (lat, lng) in enumerate(test_coords, 1):
        print(f"📍 test {i}: ({lat}, {lng})")
        
        location_type = get_location_type(lat, lng)
        print(f"   result : {location_type}")
        
        # انتظار 1 ثانية بين الطلبات (احترام rate limits)
        time.sleep(1)
        
    print("=" * 50)
    print("✅ test completed")

# النسخة المبسطة للاختبار السريع
def quick_test():
    """اختبار سريع على موقع واحد"""
    lat, lng = 41.9028, 12.4964  # روما
    result = get_location_type(lat, lng)
    print(f"📍 ({lat}, {lng}) → {result}")

# التشغيل
if __name__ == "__main__":
    # اختبار سريع أولاً
    print("🔍 fast test..")
    quick_test()
    
    # ثم الاختبار الكامل
    test_osm_api()