
import os

import psycopg

source_ds = os.environ["OLD_DB_URL"]

def check():
    try:
        with psycopg.connect(source_ds) as conn, conn.cursor() as cur:
            table = "dataapp_employeecommute"
            cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'")
            cols = [r[0] for r in cur.fetchall()]
            print(f"Columns for {table}: {cols}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check()
