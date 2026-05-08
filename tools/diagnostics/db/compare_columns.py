
import os

import psycopg

source_ds = os.environ["OLD_DB_URL"]
target_ds = os.environ["NEW_DB_URL"]

table = "dataapp_monitorsector"

try:
    s_conn = psycopg.connect(source_ds)
    t_conn = psycopg.connect(target_ds)

    s_cur = s_conn.cursor()
    t_cur = t_conn.cursor()

    s_cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position")
    s_cols = [r[0] for r in s_cur.fetchall()]

    t_cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position")
    t_cols = [r[0] for r in t_cur.fetchall()]

    print(f"Table: {table}")
    print(f"  Source columns: {s_cols}")
    print(f"  Target columns: {t_cols}")

    s_conn.close()
    t_conn.close()
except Exception as e:
    print(f"Error: {e}")
