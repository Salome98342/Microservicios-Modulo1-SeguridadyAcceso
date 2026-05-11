import urllib.request
import json

print("Testing login endpoint from host...")

url = 'http://localhost:8002/api/v1/auth/login'
payload = {'username': 'admin', 'password': 'admin123'}

body = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(
    url,
    data=body,
    method='POST',
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read().decode())
        print(f"✓ Login successful!")
        print(f"  user_id: {result.get('user_id')}")
        print(f"  role: {result.get('role')}")
        print(f"  token: {result.get('token')[:50]}...")
except urllib.error.HTTPError as e:
    error = json.loads(e.read().decode())
    print(f"✗ HTTP {e.code}: {error}")
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
