import urllib.request
import json
import sys

url = 'http://localhost:8000/api/v1/auth/login'
payload = {
    'username': 'admin',
    'password': 'admin123'
}

body = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(
    url,
    data=body,
    method='POST',
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        print(f'Status: {resp.status}')
        data = json.loads(resp.read().decode())
        print(f'Login Success!')
        print(f'  user_id: {data.get("user_id")}')
        print(f'  token: {data.get("token")[:50]}...' if data.get("token") else '  token: None')
        print(f'  role: {data.get("role")}')
except urllib.error.HTTPError as e:
    print(f'HTTP Error {e.code}')
    try:
        error_data = json.loads(e.read().decode())
        print(f'  {error_data.get("detail", str(error_data))}')
    except:
        print(f'  {e.read().decode()}')
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
    sys.exit(1)
