"""Debug map API responses"""
import urllib.request, json

def api_raw(path):
    url = f'http://localhost:8000/api/v1/map{path}'
    try:
        r = urllib.request.urlopen(url)
        data = json.loads(r.read())
        return data
    except Exception as e:
        return {'error': str(e)}

# Check geocode
print('=== Geocode ===')
r = api_raw('/geocode?address=shenyang')
print(json.dumps(r, ensure_ascii=False, indent=2)[:500])

print('\n=== Reverse Geocode ===')
r = api_raw('/reverse-geocode?latitude=41.7968&longitude=123.4497')
print(json.dumps(r, ensure_ascii=False, indent=2)[:500])

print('\n=== Distance ===')
r = api_raw('/distance?from_lat=41.7968&from_lng=123.4497&to_lat=42.5095&to_lng=123.4370')
print(json.dumps(r, ensure_ascii=False, indent=2)[:500])

print('\n=== Logistics ===')
r = api_raw('/logistics/track/ORD20240001')
print(json.dumps(r, ensure_ascii=False, indent=2)[:500])
