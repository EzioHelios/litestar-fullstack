import os
import re

sql_file = os.environ["SQL_DUMP_PATH"]
output_file = os.environ.get("VIEWS_SQL_PATH", "tools/legacy_migration/recreate_views.sql")

views_to_find = [
    "alarm_event_view", "crkje_day_sum_view", "crkje_month_sum_view", "crkje_week_sum_view",
    "crkje_year_sum_view", "hw_cdz_ammeter_day_hour_view", "hw_cdz_area_day_hour_sum_view",
    "hw_cdz_area_day_sum_view", "hw_cdz_area_month_sum_view", "hw_cdz_area_week_sum_view",
    "hw_cdz_area_year_sum_view", "hw_gf_ammeter_day_hour_view", "hw_gf_area_day_hour_sum_view",
    "hw_gf_area_day_sum_view", "hw_gf_area_month_sum_view", "hw_gf_area_week_sum_view",
    "hw_gf_area_year_sum_view", "hw_gf_day_hour_sum_view", "hw_gf_day_sum_view",
    "hw_gf_month_sum_view", "hw_gf_week_sum_view", "hw_gf_year_sum_view", "vedio_alarm_event_view",
    "yj_ammeter_day_hour_sum_view", "yj_ammeter_day_sum_view", "yj_ammeter_month_sum_view",
    "yj_ammeter_week_sum_view", "yj_ammeter_year_sum_view", "yj_area_day_hour_sum_view",
    "yj_area_day_sum_view", "yj_area_month_sum_view", "yj_area_week_sum_view",
    "yj_area_year_sum_view", "yj_day_hour_sum_view", "yj_day_sum_view", "yj_month_sum_view",
    "yj_week_sum_view", "yj_year_sum_view"
]

extracted_content = []

with open(sql_file, encoding="utf-8", errors="ignore") as f:
    content = f.read()

    # Also check if 'scope' appears anywhere
    scopes = re.findall(r"CREATE TABLE public\.(dataapp_scope\w+)", content)
    print(f"Scopes found in SQL: {scopes}")

    for view_name in views_to_find:
        # Match CREATE VIEW public.view_name AS ... ;
        # Use DOTALL to match across lines
        pattern = rf"CREATE VIEW public\.{view_name} AS(.*?);"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            print(f"Extracted view: {view_name}")
            extracted_content.append(f"DROP VIEW IF EXISTS {view_name} CASCADE;")
            extracted_content.append(f"CREATE VIEW {view_name} AS{match.group(1)};\n")
        else:
            print(f"Failed to extract view: {view_name}")

with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(extracted_content))

print(f"\nDone! Extracted {len(extracted_content)//2} views to {output_file}")
