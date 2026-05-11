import psycopg
from psycopg.rows import dict_row
import sys

print("Attempting to connect to postgres-auth...")
sys.stdout.flush()

try:
    conn = psycopg.connect("postgresql://auth:auth@postgres-auth:5432/auth_db", row_factory=dict_row, connect_timeout=3)
    print("✓ Connected!")
    
    cur = conn.cursor()
    cur.execute("SELECT 1 as test")
    result = cur.fetchone()
    print(f"✓ Query works: {result}")
    
    conn.close()
    print("✓ All good")
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
