
import os

import psycopg

source_ds = os.environ["OLD_DB_URL"]

def check():
    try:
        with psycopg.connect(source_ds) as conn, conn.cursor() as cur:
            cur.execute("SELECT MIN(reading_time), MAX(reading_time) FROM dataapp_ammeterindexvalue")
            res = cur.fetchone()
            print(f"Date range: {res}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check()
