
import psycopg

ds = "postgresql://app:app@localhost:15432/app"
try:
    conn = psycopg.connect(ds)
    cur = conn.cursor()
    # Get all tables in the public schema
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE'")
    tables = [r[0] for r in cur.fetchall()]
    print(f"Dropping tables: {tables}")
    for table in tables:
        cur.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
    conn.commit()
    print("All tables dropped successfully.")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
