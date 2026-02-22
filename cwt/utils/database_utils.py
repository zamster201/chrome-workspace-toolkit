"""
Core CRUD operations for CWT + WEM database.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "cwt_state.sqlite"

def get_connection(row_factory=False):
    conn = sqlite3.connect(DB_PATH)
    if row_factory:
        conn.row_factory = sqlite3.Row
    return conn

# Workspaces
def insert_workspace(conn, data):
    with conn:
        conn.execute(
            "INSERT INTO workspaces (name, created_at, desktop_count) VALUES (?, ?, ?)",
            (data["name"], data["created_at"], data.get("desktop_count", 0))
        )

def fetch_workspaces(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM workspaces ORDER BY created_at DESC")
    return cur.fetchall()

# Collections
def insert_collection(conn, data):
    with conn:
        conn.execute(
            "INSERT INTO collections (workspace_id, name, captured_at) VALUES (?, ?, ?)",
            (data["workspace_id"], data["name"], data["captured_at"])
        )

def fetch_collections_by_workspace(conn, workspace_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM collections WHERE workspace_id = ?", (workspace_id,))
    return cur.fetchall()

# Snapshots
def insert_snapshot(conn, data):
    with conn:
        conn.execute(
            """
            INSERT INTO snapshots (
                collection_id, app_name, window_title, hwnd,
                monitor_id, desktop_index, x, y, width, height,
                is_chrome, chrome_tabs_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["collection_id"], data["app_name"], data["window_title"], data["hwnd"],
                data["monitor_id"], data["desktop_index"], data["x"], data["y"],
                data["width"], data["height"], data.get("is_chrome", 0), data.get("chrome_tabs_json", "")
            )
        )

def fetch_snapshots_by_collection(conn, collection_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM snapshots WHERE collection_id = ?", (collection_id,))
    return cur.fetchall()

# Desktops
def insert_desktop(conn, data):
    with conn:
        conn.execute(
            "INSERT INTO desktops (workspace_id, desktop_index, name, monitor_map) VALUES (?, ?, ?, ?)",
            (data["workspace_id"], data["desktop_index"], data["name"], data.get("monitor_map", ""))
        )

def fetch_desktops_by_workspace(conn, workspace_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM desktops WHERE workspace_id = ?", (workspace_id,))
    return cur.fetchall()

# Pinned Windows
def insert_pinned_window(conn, data):
    with conn:
        conn.execute(
            "INSERT INTO pinned_windows (name, app_match, title_match, icon_path, auto_focus) VALUES (?, ?, ?, ?, ?)",
            (
                data["name"], data["app_match"], data["title_match"],
                data.get("icon_path", ""), int(data.get("auto_focus", 0))
            )
        )

def fetch_pinned_windows(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM pinned_windows ORDER BY name ASC")
    return cur.fetchall()
