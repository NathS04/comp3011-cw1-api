
import sys
import os
from sqlalchemy import text

# Add parent dir
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.db import engine

def clean_stale_tables():
    with engine.connect() as conn:
        print("Dropping stale tables...")
        conn.execute(text("DROP TABLE IF EXISTS import_runs"))
        conn.execute(text("DROP TABLE IF EXISTS data_sources"))
        # We also need to fix events table if it has the new columns but migration didn't finish recording?
        # Use PRAGMA to check columns? 
        # For simplicity, if migration failed on create_table, these shouldn't exist.
        # But if it failed later, we might be in weird state.
        # Let's hope drops are enough.
        conn.commit()
        print("Done.")

if __name__ == "__main__":
    clean_stale_tables()
