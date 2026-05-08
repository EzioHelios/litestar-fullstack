import os
import re

sql_file = os.environ["SQL_DUMP_PATH"]

tables = []
views = []

with open(sql_file, encoding="utf-8", errors="ignore") as f:
    for line in f:
        # Match CREATE TABLE public.name
        table_match = re.search(r'CREATE TABLE public\.(\w+|"[^"]+")', line)
        if table_match:
            tables.append(table_match.group(1))

        # Match CREATE VIEW public.name
        view_match = re.search(r"CREATE VIEW public\.(\w+)", line)
        if view_match:
            views.append(view_match.group(1))

print("--- ALL TABLES FOUND ---")
for t in sorted(tables):
    print(t)

print("\n--- ALL VIEWS FOUND ---")
for v in sorted(views):
    print(v)
