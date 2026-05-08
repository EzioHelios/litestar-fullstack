import os

import psycopg

source_ds = os.environ["OLD_DB_URL"]
try:
    conn = psycopg.connect(source_ds)
    cur = conn.cursor()

    # List Tables
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'")
    tables = [r[0] for r in cur.fetchall()]
    print("--- TABLES ---")
    for t in sorted(tables):
        print(f"Table: {t}")

    # List Views
    cur.execute("SELECT table_name FROM information_schema.views WHERE table_schema='public'")
    views = [r[0] for r in cur.fetchall()]
    print("\n--- VIEWS ---")
    for v in sorted(views):
        print(f"View: {v}")

    conn.close()
except Exception as e:
    print(f"Error: {e}")
