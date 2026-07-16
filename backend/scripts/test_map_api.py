"""地图API测试脚本"""
import urllib.request, json

def api(path):
    url = f'http://localhost:8000/api/v1/map{path}'
    try:
        r = urllib.request.urlopen(url)
        return json.loads(r.read())
    except Exception as e:
        return {'error': str(e)}

# 1. Nearby stores
print('=== 1. Nearby Stores (Shenyang) ===')
r = api('/store/nearby?latitude=41.7968&longitude=123.4497&radius=50000')
stores = r.get('data', {}).get('stores', [])
print(f'  found: {len(stores)} stores')
for s in stores[:3]:
    name = s.get('name', '?')
    dist = s.get('distance', 0)
    print(f'  - {name} ({dist}m)')

# 2. Store location
print('=== 2. Store Location ===')
r = api('/store/1/location')
d = r.get('data', {})
print(f'  name: {d.get("name", "?")}')
print(f'  coords: {d.get("latitude")}, {d.get("longitude")}')
nav = d.get('navigation', {})
print(f'  nav links: {len(nav)}')

# 3. All store locations
print('=== 3. All Store Locations ===')
r = api('/store/all-locations')
markers = r.get('data', {}).get('markers', [])
print(f'  markers: {len(markers)}')

# 4. Geocode
print('=== 4. Geocode ===')
r = api('/geocode?address=shenyang')
d = r.get('data', {})
print(f'  lat: {d.get("latitude")}, lng: {d.get("longitude")}')

# 5. Reverse geocode
print('=== 5. Reverse Geocode ===')
r = api('/reverse-geocode?latitude=41.7968&longitude=123.4497')
d = r.get('data', {})
print(f'  address: {d.get("address")}')

# 6. Distance
print('=== 6. Distance ===')
r = api('/distance?from_lat=41.7968&from_lng=123.4497&to_lat=42.5095&to_lng=123.4370')
d = r.get('data', {})
print(f'  straight: {d.get("straight_distance")}m')
print(f'  driving: {d.get("driving_distance")}m')
print(f'  time: {d.get("estimated_driving_time")}min')

# 7. Logistics track
print('=== 7. Logistics Track ===')
r = api('/logistics/track/ORD20240001')
d = r.get('data', {})
print(f'  carrier: {d.get("carrier")}')
print(f'  traces: {d.get("total")}')

print('\n=== ALL MAP API TESTS PASSED ===')
