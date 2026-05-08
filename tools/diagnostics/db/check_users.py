
import psycopg

ds = "postgresql://app:app@localhost:15432/app"
try:
    conn = psycopg.connect(ds)
    cur = conn.cursor()
    cur.execute("SELECT id, email FROM user_account")
    print(f"Users in Litestar: {cur.fetchall()}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
