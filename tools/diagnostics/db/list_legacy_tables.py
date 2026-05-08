
import os

import psycopg

ds = os.environ["OLD_DB_URL"]
try:
    conn = psycopg.connect(ds)
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'dataapp_%' ORDER BY table_name")
    tables = [r[0] for r in cur.fetchall()]
    print(f"DataApp tables ({len(tables)}):")
    for t in tables:
        print(f"  - {t}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
