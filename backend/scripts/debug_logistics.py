"""Debug logistics endpoint"""
import urllib.request, json

url = 'http://localhost:8000/api/v1/map/logistics/track/ORD20240001'
try:
    r = urllib.request.urlopen(url)
    print(json.loads(r.read()))
except urllib.error.HTTPError as e:
    print(f'Status: {e.code}')
    body = e.read().decode()
    print(f'Body: {body[:500]}')
