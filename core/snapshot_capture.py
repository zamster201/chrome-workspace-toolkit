# core/snapshot_capture.py

import json
import win32gui
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional
from utils.get_all_visible_windows import get_all_visible_windows
from utils.vda_utils import get_virtual_desktop_id_map


def build_snapshot_dict(workspace_name: str, timestamp: str, desktops: dict, windows: list) -> dict:
    """
    Construct the snapshot dictionary used for persistence.

    Args:
        workspace_name (str): Name of the workspace.
        timestamp (str): Timestamp string for collection ID.
        desktops (dict): Mapping of desktop index to name.
        windows (list): List of captured window metadata.

    Returns:
        dict: Fully-formed snapshot metadata dictionary.
    """
    return {
        "format_version": "1.0",
        "workspace": workspace_name,
        "collection_id": timestamp,
        "captured_at": datetime.now().isoformat(),
        "desktops": {str(i): name for i, name in desktops.items()},
        "windows": windows
    }


def capture_snapshot(workspace_name: str = "Unnamed Workspace", logger: Callable[[str], None] = print, gui_callback: Optional[Callable[[dict], None]] = None) -> str:
    """
    Captures the current window layout and desktop mapping into a snapshot file,
    including window Z-order.

    Args:
        workspace_name (str): Logical name used to group snapshots under a directory.
        logger (Callable[[str], None]): Logging function for status messages.
        gui_callback (Callable[[dict], None], optional): Optional GUI hook to report summary metadata.

    Returns:
        str: The full path to the saved snapshot file.
    """
    snapshot_dir = Path("storage/snapshots") / workspace_name
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%b%d%y_%H%M")
    snapshot_name = f"snapshot_{timestamp}.json"
    snapshot_path = snapshot_dir / snapshot_name

    logger("[INFO] Starting window enumeration and desktop mapping.")
    visible_windows = get_all_visible_windows()
    desktop_map = get_virtual_desktop_id_map()

    # Build a z-order mapping
    hwnd_order = []
    hwnd = win32gui.GetTopWindow(0)
    while hwnd:
        hwnd_order.append(hwnd)
        hwnd = win32gui.GetWindow(hwnd, win32gui.GW_HWNDNEXT)

    hwnd_rank = {h: i for i, h in enumerate(hwnd_order)}

    for win in visible_windows:
        win["z_order"] = hwnd_rank.get(win["hwnd"], -1)

    # Sort by descending z_order so topmost windows come first
    visible_windows.sort(key=lambda w: w.get("z_order", -1))

    snapshot = build_snapshot_dict(
        workspace_name=workspace_name,
        timestamp=timestamp,
        desktops=desktop_map,
        windows=visible_windows
    )

    with snapshot_path.open("w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)
        f.write("\n")  # Ensures newline at EOF

    logger(f"[📸] Captured snapshot to: {snapshot_path}")

    # This block dispatches summary metadata to the GUI.
    # Ensure the receiving GUI element is initialized before snapshot to avoid NoneType issues.
    if gui_callback:
        gui_callback({
            "workspace": workspace_name,
            "collection_id": timestamp,
            "captured_at": snapshot["captured_at"],
            "desktop_count": len(desktop_map),
            "desktop_names": list(desktop_map.values())
            # Consider extending this metadata structure in the future
            # to support active app listing or monitor layout info.
        })

    return str(snapshot_path)
