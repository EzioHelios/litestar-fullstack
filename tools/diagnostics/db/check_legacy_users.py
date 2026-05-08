
import os

import psycopg

ds = os.environ["OLD_DB_URL"]
try:
    conn = psycopg.connect(ds)
    cur = conn.cursor()
    cur.execute("SELECT id, username, email FROM auth_user")
    print(f"Users in legacy Django: {cur.fetchall()}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
