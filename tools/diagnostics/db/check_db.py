import psycopg

try:
    ds = "postgresql://app:app@localhost:15432/app"
    conn = psycopg.connect(ds)
    print("Connection successful")
    tables = conn.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'").fetchall()
    print("Tables:", [r[0] for r in tables])
    locks = conn.execute("SELECT pid, locktype, mode, granted FROM pg_locks WHERE NOT granted").fetchall()
    print("Locks:", locks)
    conn.close()
except Exception as e:
    print("Error:", e)
