
import os

import psycopg

source_ds = os.environ["OLD_DB_URL"]

def check():
    try:
        with psycopg.connect(source_ds) as conn, conn.cursor() as cur:
            table = "dataapp_monitorsectorphoto"
            cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}'")
            cols = cur.fetchall()
            print(f"Columns for {table}: {cols}")

            cur.execute(f"SELECT * FROM {table} LIMIT 1")
            row = cur.fetchone()
            print(f"Sample row: {row}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check()
