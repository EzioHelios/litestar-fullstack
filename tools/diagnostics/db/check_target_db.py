
import psycopg

db_url = "postgresql://app:app@localhost:15432/app"

try:
    with psycopg.connect(db_url) as conn, conn.cursor() as cur:
        cur.execute("""
                SELECT table_name, table_type
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_type, table_name;
            """)
        tables = cur.fetchall()
        print("--- TARGET OBJECTS ---")
        for t in tables:
            print(f"{t[1]:<15} | {t[0]}")
except Exception as e:
    print(f"Error: {e}")
