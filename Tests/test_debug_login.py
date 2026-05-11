import urllib.request
import json
import sys

print("Testing login flow step by step...\n")

# Step 1: Verify credentials  
print("1. Testing credential verification...")
url = 'http://ms-usuarios:8000/internal/users/credentials/verify'
payload = {'username': 'admin', 'encrypted_password': 'admin123', 'request_trace_id': 'test'}
body = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(url, data=body, method='POST', headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req, timeout=3) as resp:
        result = json.loads(resp.read().decode())
        print(f"   ✓ OK: {result}\n")
except Exception as e:
    print(f"   ✗ FAILED: {e}\n")
    sys.exit(1)

# Step 2: Get user permissions
print("2. Testing get permissions...")
try:
    resp = urllib.request.urlopen('http://ms-roles:8003/internal/roles/users/5/permissions', timeout=3)
    result = json.loads(resp.read().decode())
    print(f"   ✓ OK: role={result.get('role')}, perms={len(result.get('permissions', []))}\n")
except Exception as e:
    print(f"   ✗ FAILED: {e}\n")
    sys.exit(1)

# Step 3: Try login (will timeout)
print("3. Testing login endpoint (5sec timeout)...")
url = 'http://localhost:8000/api/v1/auth/login'
payload = {'username': 'admin', 'password': 'admin123'}
body = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(url, data=body, method='POST', headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req, timeout=5) as resp:
        result = json.loads(resp.read().decode())
        print(f"   ✓ OK: user_id={result.get('user_id')}, token={result.get('token')[:30]}...\n")
except urllib.error.HTTPError as e:
    print(f"   ✗ HTTP {e.code}: {e.read().decode()}\n")
except Exception as e:
    print(f"   ✗ TIMEOUT/ERROR: {type(e).__name__}\n")

print("Done!")
