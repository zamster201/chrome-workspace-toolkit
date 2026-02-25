
"""
Database interface for CWT + WEM.
Handles initialization, connection, and basic access utilities.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "cwt_state.sqlite"
SCHEMA_PATH = Path(__file__).resolve().parent / "cwt_schema.sql"


def get_connection():
    """Returns a SQLite connection to the primary DB."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def initialize_database():
    """Creates the DB schema if it doesn't already exist."""
    if not DB_PATH.exists():
        print("📦 Initializing new CWT database...")
        conn = get_connection()
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
    else:
        print("🧠 Existing database detected — skipping schema init.")


# Optional test: run from terminal
if __name__ == "__main__":
    initialize_database()
    print("✅ Database ready at:", DB_PATH)
