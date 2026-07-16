"""API联调测试脚本"""
import urllib.request, json

def api(path, token=None, method='GET', data=None):
    url = f'http://localhost:8000/api/v1{path}'
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header('Content-Type', 'application/json')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    try:
        r = urllib.request.urlopen(req)
        return json.loads(r.read())
    except Exception as e:
        return {'error': str(e)}

# 1. Login
print('=== 1. Login ===')
res = api('/auth/login', method='POST', data={'phone':'13800000001','password':'123456'})
token = res.get('access_token','')
print(f'  token: {token[:20]}...' if token else f'  FAIL: {res}')

# 2. Products
print('=== 2. Products ===')
r = api('/product/list?page=1&size=5')
items = r.get('items', [])
print(f'  count: {len(items)}')
if items:
    print(f'  first: {items[0]["name"]}')

# 3. Banners
print('=== 3. Banners ===')
r = api('/banner/list?position=home')
items = r.get('items', [])
print(f'  count: {len(items)}')

# 4. Announcements
print('=== 4. Announcements ===')
r = api('/announcement/list?page=1')
items = r.get('items', [])
print(f'  count: {len(items)}')

# 5. Group Buy Sessions
print('=== 5. Group Buy Sessions ===')
r = api('/group-buy/sessions', token)
items = r.get('items', r.get('sessions', []))
print(f'  count: {len(items)}')

# 6. Stores
print('=== 6. Stores ===')
r = api('/store/list')
items = r.get('items', r.get('stores', []))
print(f'  count: {len(items)}')

# 7. Cart (add + list)
print('=== 7. Cart ===')
r = api('/cart/list', token)
cart_items = r.get('items', [])
print(f'  existing cart: {len(cart_items)}')

# 8. Addresses
print('=== 8. Addresses ===')
r = api('/address/list', token)
addrs = r.get('items', [])
print(f'  count: {len(addrs)}')

# 9. Orders
print('=== 9. Orders ===')
r = api('/order/list?page=1&size=5', token)
orders = r.get('orders', [])
print(f'  count: {len(orders)}')

print('\n=== ALL API TESTS DONE ===')
