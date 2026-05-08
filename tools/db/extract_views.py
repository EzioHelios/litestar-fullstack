
import re
from pathlib import Path

sql_file = Path(r'C:\Users\ASUS\Desktop\project1\xtck_deploy\xtck_deploy\db_xtck_20260203.sql')
output_file = Path(r'C:\Users\ASUS\Desktop\project1\litestar-fullstack\tools\db\recreate_views.sql')

output_file.parent.mkdir(parents=True, exist_ok=True)

with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f, \
     open(output_file, 'w', encoding='utf-8') as out:
    
    in_view = False
    current_view = []
    
    for line in f:
        if 'CREATE VIEW' in line:
            in_view = True
            current_view = [line]
            if ';' in line:
                out.write("".join(current_view) + "\n\n")
                in_view = False
        elif in_view:
            current_view.append(line)
            if ';' in line:
                out.write("".join(current_view) + "\n\n")
                in_view = False

print(f"Extracted views to {output_file}")
