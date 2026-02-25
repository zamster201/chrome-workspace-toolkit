# core/restore.py

import json
import traceback
import win32gui
import win32con
import win32api
from fuzzywuzzy import fuzz
from pathlib import Path
from pyvda import AppView, get_virtual_desktops
from cwt.utils.get_all_visible_windows import get_all_visible_windows
from cwt.utils.vda_utils import get_current_virtual_desktop_id

# Future: make this a .windowignore file
IGNORED_PROCESSES = {"VoiceAccess.exe", "explorer.exe"}


def get_monitor_bounds():
    """
    Returns the union bounding box across all connected monitors as
    (x_min, y_min, x_max, y_max) in physical pixels.
    """
    monitors = win32api.EnumDisplayMonitors()
    x_min = min(r[0] for _, _, r in monitors)
    y_min = min(r[1] for _, _, r in monitors)
    x_max = max(r[2] for _, _, r in monitors)
    y_max = max(r[3] for _, _, r in monitors)
    return x_min, y_min, x_max, y_max


def is_within_bounds(x, y, width, height, bounds):
    """
    Returns True if the window's top-left anchor falls within the usable
    monitor space. A 20px margin is applied so partially off-screen windows
    still have a grabbable title bar.
    """
    x_min, y_min, x_max, y_max = bounds
    MARGIN = 20
    return (
        x_min - MARGIN <= x <= x_max - MARGIN and
        y_min <= y <= y_max - MARGIN
    )

def move_and_resize(hwnd, x, y, width, height, logger=print):
    """
    Restores and repositions a window to the specified coordinates and size.

    Args:
        hwnd (int): Window handle.
        x (int): X coordinate of the upper-left corner.
        y (int): Y coordinate of the upper-left corner.
        width (int): Desired window width.
        height (int): Desired window height.
        logger (Callable): Logging function for status output.
    """
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.MoveWindow(hwnd, x, y, width, height, True)
        win32gui.SetForegroundWindow(hwnd)
    except Exception as e:
        logger(f"[!] MoveWindow failed for hwnd {hwnd}: {e}")
        logger(traceback.format_exc())

def load_snapshot(snapshot_path):
    with open(snapshot_path, "r", encoding="utf-8") as f:
        return json.load(f)

def match_windows(snapshot, current_windows, threshold):
    """
    Performs fuzzy matching between saved snapshot windows and currently visible windows.

    Args:
        snapshot (dict): Snapshot data containing saved window entries.
        current_windows (list): List of currently visible windows.
        threshold (int): Matching score threshold to consider a window a valid match.

    Returns:
        list: Tuples of (snapshot_window, matched_live_window, match_score)
    """
    matches = []
    for snap_win in snapshot["windows"]:
        best_match = None
        best_score = 0
        for live_win in current_windows:
            if snap_win["exe"].lower() == live_win["exe"].lower():
                score = fuzz.partial_ratio(snap_win["title"], live_win["title"])
                if score > best_score:
                    best_score = score
                    best_match = live_win
        matches.append((snap_win, best_match, best_score))
    return matches

def resolve_desktop(snap_win, logger):
    desktops = get_virtual_desktops()
    for d in desktops:
        if str(d.id) == snap_win.get("desktop_id"):
            return d
    index = snap_win.get("desktop_number")
    if isinstance(index, int) and 0 < index <= len(desktops):
        try:
            return desktops[index - 1]
        except Exception as e:
            logger(f"[!] Failed to resolve desktop index {index} for {snap_win.get('title', '')}: {e}")
    return None

def restore_window_layout(matches, threshold, logger):
    bounds = get_monitor_bounds()
    logger(f"[🖥️] Monitor bounds: x={bounds[0]}→{bounds[2]}, y={bounds[1]}→{bounds[3]}")

    for snap_win, live_win, score in matches:
        if score >= threshold and live_win:
            if snap_win.get("exe") in IGNORED_PROCESSES:
                logger(f"[!] Skipping known system window: {snap_win['exe']}")
                continue

            x, y, w, h = snap_win["x"], snap_win["y"], snap_win["width"], snap_win["height"]

            if not is_within_bounds(x, y, w, h, bounds):
                logger(f"[⚠️] Out of bounds — skipping: '{snap_win['title']}' @ ({x}, {y}) {w}×{h}")
                continue

            hwnd = live_win["hwnd"]
            move_and_resize(hwnd, x, y, w, h, logger)
            target_desktop = resolve_desktop(snap_win, logger)
            if target_desktop:
                try:
                    AppView(hwnd).move(target_desktop)
                except Exception as e:
                    logger(f"[!] Failed to move hwnd {hwnd} to desktop: {e}")
                    logger(traceback.format_exc())
            logger(f"[✓] {snap_win['title']} → {live_win['title']} (score: {score})")
        else:
            logger(f"[!] No match: {snap_win['title']} (best: {score})")

def restore_windows(snapshot_path, threshold=85, return_to_origin=True, logger=print):
    """
    Restores a captured workspace snapshot by matching saved windows to current ones,
    moving them to their original positions, and optionally reassigning them to their
    original virtual desktops. Also returns to the starting desktop if requested.

    Args:
        snapshot_path (str): Path to the snapshot JSON file.
        threshold (int): Fuzzy match threshold for window comparison (0–100).
        return_to_origin (bool): Whether to return to the original desktop after restore.
        logger (Callable): Logging function for status messages.
    """
    snapshot = load_snapshot(snapshot_path)
    current_windows = get_all_visible_windows()
    start_desktop = get_current_virtual_desktop_id()

    ws_name = snapshot.get("workspace", "Unnamed Workspace")
    desktops = snapshot.get("desktops", {})
    desktop_count = len(desktops)
    desktop_labels = list(desktops.values())

    logger(f"\n📂 Workspace: {ws_name}")
    logger(f"🖥️ Desktops: {desktop_count} — {' | '.join(desktop_labels)}\n")

    matches = match_windows(snapshot, current_windows, threshold)
    restore_window_layout(matches, threshold, logger)

    if return_to_origin:
        try:
            for d in get_virtual_desktops():
                if str(d.id) == start_desktop:
                    d.go()
                    logger("[↩] Returned to starting desktop")
                    break
        except Exception as e:
            logger(f"[!] Could not return to origin: {e}")
            logger(traceback.format_exc())