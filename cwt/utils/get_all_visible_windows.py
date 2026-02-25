# utils/get_all_visible_windows.py

import win32gui
import win32process
import psutil
from pyvda import AppView, get_virtual_desktops
from cwt.utils.debug_logger import log_debug, log_info, log_error

def get_all_visible_windows():
    log_info("Starting window enumeration and desktop mapping.")

    def is_real_window(hwnd):
        if not win32gui.IsWindowVisible(hwnd):
            return False
        if win32gui.GetParent(hwnd) != 0:
            return False
        title = win32gui.GetWindowText(hwnd)
        if not title:
            return False
        return True

    def get_exe(hwnd):
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            return psutil.Process(pid).name()
        except Exception:
            return ""

    desktops = get_virtual_desktops()
    desktop_guid_to_number = {
        str(vd.id): i + 1 for i, vd in enumerate(desktops)
    }
    desktop_guid_to_name = {
        str(vd.id): vd.name or f"Desktop #{i + 1}"
        for i, vd in enumerate(desktops)
    }

    hwnds = []
    win32gui.EnumWindows(lambda hwnd, param: param.append(hwnd), hwnds)
    visible_hwnds = [hwnd for hwnd in hwnds if is_real_window(hwnd)]

    windows = []
    for hwnd in visible_hwnds:
        win_title = win32gui.GetWindowText(hwnd)
        rect = win32gui.GetWindowRect(hwnd)
        exe = get_exe(hwnd)

        desktop_number = None
        desktop_name = "Unknown"
        try:
            app = AppView(hwnd)
            for vd in desktops:
                if app.is_on_desktop(vd):
                    guid = str(vd.id)
                    desktop_number = desktop_guid_to_number.get(guid)
                    desktop_name = desktop_guid_to_name.get(guid, f"Desktop {guid}")
                    break
        except Exception as e:
            log_debug(f"[SKIP] '{win_title}' ({exe}) — not assignable to virtual desktop, skipping.")

        windows.append({
            "hwnd": hwnd,
            "title": win_title,
            "exe": exe,
            "x": rect[0],
            "y": rect[1],
            "width": rect[2] - rect[0],
            "height": rect[3] - rect[1],
            "desktop_number": desktop_number,
            "desktop_name": desktop_name
        })

    log_info(f"Enumerated {len(windows)} visible windows.")
    return windows