# core/snapshot_capture.py

import json
import uuid
import win32gui
import win32con
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional
from cwt.utils.get_all_visible_windows import get_all_visible_windows
from cwt.utils.vda_utils import get_virtual_desktop_id_map
from cwt.utils.paths import get_snapshots_dir


def build_snapshot_dict(collection_name: str, collection_id: str, timestamp: str, desktops: dict, windows: list) -> dict:
    return {
        "format_version": "1.0",
        "collection_name": collection_name,
        "collection_id": collection_id,
        "captured_at": datetime.now().strftime("%d-%b-%Y %H:%M"),
        "desktops": {str(i): name for i, name in desktops.items()},
        "windows": windows
    }


def capture_snapshot(
    collection_name: str = "Unnamed Collection",
    logger: Callable[[str], None] = print,
    gui_callback: Optional[Callable[[dict], None]] = None,
    chrome_only: bool = False,
    app_only: bool = False
) -> str:
    """
    Captures the current window layout into a snapshot file.

    Args:
        collection_name: Name used to group snapshots under a directory.
        logger: Logging function for status messages.
        gui_callback: Optional GUI hook to report summary metadata.
        chrome_only: If True, capture only Chrome windows.
        app_only: If True, capture only non-Chrome windows.

    Returns:
        str: Full path to the saved snapshot file.
    """
    snapshot_dir = get_snapshots_dir() / collection_name
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%d-%b-%Y_%H%M")
    collection_id = str(uuid.uuid4())
    snapshot_path = snapshot_dir / f"snapshot_{timestamp}.json"

    logger("[INFO] Starting window enumeration and desktop mapping.")
    visible_windows = get_all_visible_windows()
    desktop_map = get_virtual_desktop_id_map()

    # Apply capture filters
    if chrome_only:
        visible_windows = [w for w in visible_windows if "chrome" in w.get("exe", "").lower()]
        logger(f"[INFO] Chrome-only filter applied — {len(visible_windows)} windows retained.")
    elif app_only:
        visible_windows = [w for w in visible_windows if "chrome" not in w.get("exe", "").lower()]
        logger(f"[INFO] Apps-only filter applied — {len(visible_windows)} windows retained.")

    # Build z-order mapping
    hwnd_order = []
    hwnd = win32gui.GetTopWindow(0)
    while hwnd:
        hwnd_order.append(hwnd)
        hwnd = win32gui.GetWindow(hwnd, win32con.GW_HWNDNEXT)

    hwnd_rank = {h: i for i, h in enumerate(hwnd_order)}
    for win in visible_windows:
        win["z_order"] = hwnd_rank.get(win["hwnd"], -1)
    visible_windows.sort(key=lambda w: w.get("z_order", -1))

    snapshot = build_snapshot_dict(
        collection_name=collection_name,
        collection_id=collection_id,
        timestamp=timestamp,
        desktops=desktop_map,
        windows=visible_windows
    )

    with snapshot_path.open("w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)
        f.write("\n")

    logger(f"[📸] Captured snapshot to: {snapshot_path}")

    if gui_callback:
        gui_callback({
            "collection_name": collection_name,
            "collection_id": collection_id,
            "captured_at": snapshot["captured_at"],
            "desktop_count": len(desktop_map),
            "desktop_names": list(desktop_map.values())
        })

    return str(snapshot_path)