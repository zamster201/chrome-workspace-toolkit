
-- Workspace definitions
CREATE TABLE workspaces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TEXT,
    desktop_count INTEGER
);

-- Virtual desktop layout per workspace
CREATE TABLE desktops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id INTEGER,
    desktop_index INTEGER,
    name TEXT,
    monitor_map TEXT,
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
);

-- Groupings of window snapshots
CREATE TABLE collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id INTEGER,
    name TEXT NOT NULL,
    captured_at TEXT,
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
);

-- One snapshot per open window
CREATE TABLE snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER,
    app_name TEXT,
    window_title TEXT,
    hwnd INTEGER,
    monitor_id INTEGER,
    desktop_index INTEGER,
    x INTEGER,
    y INTEGER,
    width INTEGER,
    height INTEGER,
    is_chrome BOOLEAN,
    chrome_tabs_json TEXT,
    FOREIGN KEY (collection_id) REFERENCES collections(id)
);

-- Persistent pinned window definitions (for WEM/MiniBar)
CREATE TABLE pinned_windows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    app_match TEXT,
    title_match TEXT,
    icon_path TEXT,
    auto_focus BOOLEAN DEFAULT 0
);

-- Global settings or preferences
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
