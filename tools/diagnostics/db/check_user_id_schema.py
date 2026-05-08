
import psycopg

ds = "postgresql://app:app@localhost:15432/app"
try:
    conn = psycopg.connect(ds)
    cur = conn.cursor()
    cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'user_account' AND column_name = 'id'")
    print(f"User account ID schema: {cur.fetchall()}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
