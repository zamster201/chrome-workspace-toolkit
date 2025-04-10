# core/restore.py

import json
import traceback
import win32gui
import win32con
from fuzzywuzzy import fuzz
from pyvda import AppView, get_virtual_desktops
from utils.get_all_visible_windows import get_all_visible_windows
from utils.vda_utils import get_current_virtual_desktop_id

# Future: make this a .windowignore file
IGNORED_PROCESSES = {"VoiceAccess.exe", "explorer.exe"}

def move_and_resize(hwnd, x, y, width, height, logger=print):
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
    for snap_win, live_win, score in matches:
        if score >= threshold and live_win:
            if snap_win.get("exe") in IGNORED_PROCESSES:
                logger(f"[!] Skipping known system window: {snap_win['exe']}")
                continue
            hwnd = live_win["hwnd"]
            move_and_resize(hwnd, snap_win["x"], snap_win["y"], snap_win["width"], snap_win["height"], logger)
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
