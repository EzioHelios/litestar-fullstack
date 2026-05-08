
import os

import psycopg

source_ds = os.environ["OLD_DB_URL"]

def check():
    try:
        with psycopg.connect(source_ds) as conn, conn.cursor() as cur:
            cur.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'")
            tables = [r[0] for r in cur.fetchall()]
            print(f"Found {len(tables)} tables in source")
            for table in sorted(tables):
                if "scope" in table.lower() or "dataapp" in table.lower():
                    cur.execute(f"SELECT count(*) FROM {table}")
                    count = cur.fetchone()[0]
                    print(f"{table}: {count}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check()
