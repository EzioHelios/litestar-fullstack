
import contextlib

# Import the migrate function
from migrate_data import migrate

# Redirect stdout to a file
with open("migration_debug_out.log", "w", encoding="utf-8") as f, contextlib.redirect_stdout(f):
    with contextlib.redirect_stderr(f):
        migrate()
print("Migration debug finished. Check migration_debug_out.log")
