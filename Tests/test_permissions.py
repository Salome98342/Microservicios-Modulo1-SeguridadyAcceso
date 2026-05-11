import urllib.request
import json

try:
    resp = urllib.request.urlopen('http://ms-roles:8003/internal/roles/users/5/permissions', timeout=3)
    print(f'Status: {resp.status}')
    data = json.loads(resp.read().decode())
    print('Response:')
    print(f'  Role: {data.get("role")}')
    print(f'  Permissions count: {len(data.get("permissions", []))}')
    print(f'  First permission: {data.get("permissions", [None])[0] if data.get("permissions") else "None"}')
except urllib.error.HTTPError as e:
    print(f'HTTP Error {e.code}: {e.read().decode()}')
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
