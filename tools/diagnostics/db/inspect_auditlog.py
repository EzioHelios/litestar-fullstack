
import os

import psycopg

ds = os.environ["OLD_DB_URL"]
try:
    conn = psycopg.connect(ds)
    cur = conn.cursor()
    cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'dataapp_auditlog' ORDER BY ordinal_position")
    cols = cur.fetchall()
    print("Columns for dataapp_auditlog:")
    for col in cols:
        print(f"  - {col[0]}: {col[1]}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
