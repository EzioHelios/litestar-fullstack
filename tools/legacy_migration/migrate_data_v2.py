
import datetime
import json
import os
import sys
from pathlib import Path
from uuid import uuid4

import psycopg

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src" / "py"))

from app.lib.settings import get_settings

# Use settings for target database
settings = get_settings()
target_ds = settings.db.URL.replace("postgresql+asyncpg://", "postgresql://").replace("postgresql+psycopg://", "postgresql://")
source_ds = os.environ["OLD_DB_URL"]

def migrate():
    try:
        print(f"Connecting to source: {source_ds}")
        print(f"Connecting to target: {target_ds}")

        s_conn = psycopg.connect(source_ds)
        t_conn = psycopg.connect(target_ds)

        s_cur = s_conn.cursor()
        t_cur = t_conn.cursor()

        t_cur.execute("SET session_replication_role = 'replica'")

        # 1. Migrate Users
        print("Migrating users...")
        s_cur.execute("SELECT id, username, email, is_active, is_superuser, date_joined FROM auth_user")
        users = s_cur.fetchall()
        user_id_map = {}
        for u_id, username, email, is_active, is_superuser, joined_at in users:
            new_id = uuid4()
            user_id_map[u_id] = new_id
            now = datetime.datetime.now(datetime.UTC)
            t_cur.execute("SELECT id FROM user_account WHERE username = %s", (username,))
            res = t_cur.fetchone()
            if not res:
                t_cur.execute(
                    "INSERT INTO user_account (id, username, email, is_active, is_superuser, is_verified, joined_at, created_at, updated_at, login_count, failed_reset_attempts, is_two_factor_enabled) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (new_id, username, email, is_active, is_superuser, True, joined_at.date(), now, now, 0, 0, False)
                )
            else:
                user_id_map[u_id] = res[0]

        # 2. Independent Tables

        # EnterpriseInfo
        print("Migrating EnterpriseInfo...")
        s_cur.execute("SELECT * FROM dataapp_enterpriseinfo")
        rows = s_cur.fetchall()
        t_cur.execute("TRUNCATE dataapp_enterpriseinfo CASCADE")
        for row in rows:
            # Source cols: id, name, belong_unit, people_count, verify_code, industry, store_area, green_area, location, other_info
            # Assuming same order as target check for now or at least first few
            t_cur.execute(
                "INSERT INTO dataapp_enterpriseinfo (name, belong_unit, people_count, unify_code) VALUES (%s, %s, %s, %s)",
                (row[1], row[2], row[3], row[4])
            )

        # MonitorSector
        print("Migrating MonitorSector...")
        s_cur.execute("SELECT code, name, area, description, area_id, is_enable FROM dataapp_monitorsector")
        sectors = s_cur.fetchall()
        sector_code_map = {}
        t_cur.execute("TRUNCATE dataapp_monitorsector CASCADE")
        for code, name, area, desc, area_id, is_enable in sectors:
            t_cur.execute(
                "INSERT INTO dataapp_monitorsector (code, name, area, description, area_id, is_enable) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                (code, name, area, desc, area_id, is_enable)
            )
            new_id = t_cur.fetchone()[0]
            sector_code_map[code] = new_id

        # VideoMonitor
        print("Migrating VideoMonitor...")
        s_cur.execute("SELECT * FROM dataapp_videomonitor")
        vm_cols = [desc[0] for desc in s_cur.description]
        vms = s_cur.fetchall()
        t_cur.execute("TRUNCATE dataapp_videomonitor CASCADE")
        for row in vms:
            row_dict = dict(zip(vm_cols, row))
            t_cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'dataapp_videomonitor'")
            target_cols = [r[0] for r in t_cur.fetchall()]
            common = [c for c in vm_cols if c in target_cols]
            q = f"INSERT INTO dataapp_videomonitor ({','.join(common)}) VALUES ({','.join(['%s']*len(common))})"
            t_cur.execute(q, [row_dict[c] for c in common])

        # 3. Dependent Tables

        # MonitorEquipment
        print("Migrating MonitorEquipment...")
        s_cur.execute("SELECT * FROM dataapp_monitorequipment")
        me_cols = [desc[0] for desc in s_cur.description]
        mes = s_cur.fetchall()
        equipment_code_map = {}
        t_cur.execute("TRUNCATE dataapp_monitorequipment CASCADE")
        for row in mes:
            row_dict = dict(zip(me_cols, row))
            source_sector_code = row_dict.get("sector_id")
            row_dict["sector_id"] = sector_code_map.get(source_sector_code)

            t_cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'dataapp_monitorequipment'")
            target_cols = [r[0] for r in t_cur.fetchall()]
            common = [c for c in me_cols if c in target_cols]
            q = f"INSERT INTO dataapp_monitorequipment ({','.join(common)}) VALUES ({','.join(['%s']*len(common))}) RETURNING id"
            t_cur.execute(q, [row_dict[c] for c in common])
            new_id = t_cur.fetchone()[0]
            equipment_code_map[row_dict["code"]] = new_id

        # MonitorSectorPhoto
        print("Migrating MonitorSectorPhoto...")
        s_cur.execute("SELECT * FROM dataapp_monitorsectorphoto")
        msp_cols = [desc[0] for desc in s_cur.description]
        msps = s_cur.fetchall()
        t_cur.execute("TRUNCATE dataapp_monitorsectorphoto CASCADE")
        for row in msps:
            row_dict = dict(zip(msp_cols, row))
            source_sector_code = row_dict.get("sector_id")
            row_dict["sector_id"] = sector_code_map.get(source_sector_code)
            t_cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'dataapp_monitorsectorphoto'")
            target_cols = [r[0] for r in t_cur.fetchall()]
            common = [c for c in msp_cols if c in target_cols]
            q = f"INSERT INTO dataapp_monitorsectorphoto ({','.join(common)}) VALUES ({','.join(['%s']*len(common))})"
            t_cur.execute(q, [row_dict[c] for c in common])

        # WarningRule
        print("Migrating WarningRule...")
        s_cur.execute("SELECT * FROM dataapp_warningrule")
        wr_cols = [desc[0] for desc in s_cur.description]
        wrs = s_cur.fetchall()
        warning_rule_map = {}
        t_cur.execute("TRUNCATE dataapp_warningrule CASCADE")
        for row in wrs:
            row_dict = dict(zip(wr_cols, row))
            row_dict["sector_id"] = sector_code_map.get(row_dict.get("sector_id"))
            if isinstance(row_dict.get("range_val"), dict):
                row_dict["range_val"] = json.dumps(row_dict["range_val"])
            t_cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'dataapp_warningrule'")
            target_cols = [r[0] for r in t_cur.fetchall()]
            common = [c for c in wr_cols if c in target_cols]
            q = f"INSERT INTO dataapp_warningrule ({','.join(common)}) VALUES ({','.join(['%s']*len(common))}) RETURNING id"
            t_cur.execute(q, [row_dict[c] for c in common])
            warning_rule_map[row_dict["id"]] = t_cur.fetchone()[0]

        # AlarmEvent
        print("Migrating AlarmEvent...")
        s_cur.execute("SELECT * FROM dataapp_alarmevent")
        ae_cols = [desc[0] for desc in s_cur.description]
        aes = s_cur.fetchall()
        t_cur.execute("TRUNCATE dataapp_alarmevent CASCADE")
        for row in aes:
            row_dict = dict(zip(ae_cols, row))
            row_dict["sector_id"] = sector_code_map.get(row_dict.get("sector_id"))
            row_dict["equipment_id"] = equipment_code_map.get(row_dict.get("equipment_id"))
            row_dict["rule_id"] = warning_rule_map.get(row_dict.get("rule_id"))
            t_cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'dataapp_alarmevent'")
            target_cols = [r[0] for r in t_cur.fetchall()]
            common = [c for c in ae_cols if c in target_cols]
            q = f"INSERT INTO dataapp_alarmevent ({','.join(common)}) VALUES ({','.join(['%s']*len(common))})"
            t_cur.execute(q, [row_dict[c] for c in common])

        # AmmeterIndexValue
        t_cur.execute("SELECT count(*) FROM dataapp_ammeterindexvalue")
        target_count = t_cur.fetchone()[0]
        if target_count < 1000000:
             print("Migrating AmmeterIndexValue (Full)...")
             t_cur.execute("TRUNCATE dataapp_ammeterindexvalue CASCADE")
             s_cur.execute("SELECT * FROM dataapp_ammeterindexvalue")
             aiv_cols = [desc[0] for desc in s_cur.description]
             batch_size = 5000
             t_cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'dataapp_ammeterindexvalue'")
             t_cols = [r[0] for r in t_cur.fetchall()]
             common_cols = [c for c in aiv_cols if c in t_cols]
             if "equipment_id" not in common_cols: common_cols.append("equipment_id")

             insert_q = f"INSERT INTO dataapp_ammeterindexvalue ({','.join(common_cols)}) VALUES ({','.join(['%s']*len(common_cols))})"

             while True:
                 rows = s_cur.fetchmany(batch_size)
                 if not rows: break
                 vals_batch = []
                 for row in rows:
                     row_dict = dict(zip(aiv_cols, row))
                     row_dict["equipment_id"] = equipment_code_map.get(row_dict.get("ammeter_id"))
                     vals = [row_dict.get(c) for c in common_cols]
                     vals_batch.append(vals)
                 t_cur.executemany(insert_q, vals_batch)
                 t_conn.commit()
                 print(f"  Inserted {batch_size} rows...")
        else:
             print("AmmeterIndexValue already populated, skipping.")

        t_cur.execute("SET session_replication_role = 'origin'")
        t_conn.commit()
        print("Migration V2 completed successfully!")

    except Exception as e:
        print(f"Migration V2 failed: {e}")
        import traceback
        traceback.print_exc()
        if "t_conn" in locals(): t_conn.rollback()
    finally:
        if "s_conn" in locals(): s_conn.close()
        if "t_conn" in locals(): t_conn.close()

if __name__ == "__main__":
    migrate()
