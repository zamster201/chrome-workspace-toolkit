# Snapshot Capture - Chrome Workspace Toolkit (CWT)
# Captures all visible windows and desktop structure into a named workspace snapshot

import os
import json
from datetime import datetime
from pathlib import Path
from utils.get_all_visible_windows import get_all_visible_windows
from utils.vda_utils import get_virtual_desktop_id_map

def capture_snapshot(workspace_name="Unnamed_Workspace", logger=print):
    now = datetime.now()
    timestamp = now.strftime("%b%d%y_%H%M")
    snapshot_root = Path("snapshots") / workspace_name
    snapshot_root.mkdir(parents=True, exist_ok=True)

    collection_id = timestamp
    windows = get_all_visible_windows()
    desktop_map = get_virtual_desktop_id_map()

    snapshot = {
        "workspace": workspace_name,
        "collection_id": collection_id,
        "captured_at": now.isoformat(),
        "desktops": desktop_map,
        "windows": windows
    }

    filename = f"snapshot_{collection_id}.json"
    filepath = snapshot_root / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)

    logger(f"[📸] Captured snapshot to: {filepath}")
    return filepath
