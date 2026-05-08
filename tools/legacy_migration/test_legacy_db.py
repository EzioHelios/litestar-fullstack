
import os

import psycopg

ds = os.environ["OLD_DB_URL"]
try:
    conn = psycopg.connect(ds)
    print("Legacy DB connection successful!")
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' LIMIT 5")
    print(f"Sample tables: {cur.fetchall()}")
    conn.close()
except Exception as e:
    print(f"Legacy DB connection failed: {e}")
