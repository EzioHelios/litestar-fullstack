
import os

import psycopg

source_ds = os.environ["OLD_DB_URL"]

def check():
    try:
        with psycopg.connect(source_ds) as conn, conn.cursor() as cur:
            table = "dataapp_monitorsector"
            cur.execute(f"""
                    SELECT a.attname
                    FROM   pg_index i
                    JOIN   pg_attribute a ON a.attrelid = i.indrelid
                                         AND a.attnum = ANY(i.indkey)
                    WHERE  i.indrelid = '{table}'::regclass
                    AND    i.indisprimary;
                """)
            pk = [r[0] for r in cur.fetchall()]
            print(f"PK for {table}: {pk}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check()
