# Legacy Migration Tools

Utilities in this directory support one-off migration and validation work from the legacy XTCK database.

Required environment variables vary by script:

- `OLD_DB_URL`: source legacy PostgreSQL connection string.
- `NEW_DB_URL`: target PostgreSQL connection string when comparing or copying between databases.
- `DATABASE_URL`: target app database, used by scripts that load app settings.
- `SQL_DUMP_PATH`: path to a legacy SQL dump.
- `VIEWS_SQL_PATH`: optional output/input path for recreated views, defaulting to files in this directory.

These scripts are operational tooling, not application runtime code.
