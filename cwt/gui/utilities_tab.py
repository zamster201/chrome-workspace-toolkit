# gui/utilities_tab.py

"""
UtilitiesTab – Chrome Workspace Toolkit (CWT)

Provides system-level tools such as shell folder audit, default mapping restore,
and monitor layout calibration for snapshot/restore accuracy.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import winreg
import ctypes
import win32api
from cwt.utils.tooltip import ToolTip


class UtilitiesTab(ttk.Frame):
    def __init__(self, master, advanced_mode):
        super().__init__(master)
        self.advanced_mode = advanced_mode
        self._build_ui()

    def _build_ui(self):
        # ── Shell Folder Audit ──────────────────────────────────────────────
        ttk.Label(self, text="🧰 Shell Folder Audit & Remap", font=("Segoe UI", 11, "bold")).pack(pady=(12, 4))

        self.adv_check = ttk.Checkbutton(self, text="Advanced Mode", variable=self.advanced_mode)
        self.adv_check.pack(anchor="w", padx=14)

        self.folder_tree = ttk.Treeview(self, columns=("Name", "Status", "Path"), show="headings", height=7)
        self.folder_tree.heading("Name", text="Folder")
        self.folder_tree.heading("Status", text="Status")
        self.folder_tree.heading("Path", text="Path")
        self.folder_tree.column("Name", width=90, anchor="w")
        self.folder_tree.column("Status", width=90, anchor="center")
        self.folder_tree.column("Path", width=350)
        self.folder_tree.pack(pady=4, padx=14)

        btn_row = tk.Frame(self)
        btn_row.pack(pady=4)

        refresh_btn = ttk.Button(btn_row, text="🔄 Refresh Status", command=self.refresh_shell_audit)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(refresh_btn, "Re-scan current user shell folder paths")

        restore_btn = ttk.Button(btn_row, text="🚰 Restore Defaults", command=self.restore_shell_defaults)
        restore_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(restore_btn, "Restore system folder mappings to local user profile")

        self.refresh_shell_audit()

        # ── Monitor Calibration ─────────────────────────────────────────────
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=14, pady=(10, 6))

        ttk.Label(self, text="🖥️ Monitor Layout & Calibration", font=("Segoe UI", 11, "bold")).pack(pady=(0, 4))

        self.monitor_tree = ttk.Treeview(
            self,
            columns=("Monitor", "Resolution", "Position", "DPI", "Primary"),
            show="headings",
            height=4
        )
        self.monitor_tree.heading("Monitor",    text="Monitor")
        self.monitor_tree.heading("Resolution", text="Resolution")
        self.monitor_tree.heading("Position",   text="Top-Left")
        self.monitor_tree.heading("DPI",        text="DPI Scale")
        self.monitor_tree.heading("Primary",    text="Primary")
        self.monitor_tree.column("Monitor",    width=80,  anchor="center")
        self.monitor_tree.column("Resolution", width=110, anchor="center")
        self.monitor_tree.column("Position",   width=100, anchor="center")
        self.monitor_tree.column("DPI",        width=80,  anchor="center")
        self.monitor_tree.column("Primary",    width=60,  anchor="center")
        self.monitor_tree.pack(pady=4, padx=14)

        mon_btn_row = tk.Frame(self)
        mon_btn_row.pack(pady=4)

        scan_btn = ttk.Button(mon_btn_row, text="🔍 Scan Monitors", command=self.refresh_monitor_info)
        scan_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(scan_btn, "Detect all connected monitors and their coordinate layout")

        self.refresh_monitor_info()

    # ── Shell Folder Methods ────────────────────────────────────────────────

    def refresh_shell_audit(self):
        self.folder_tree.delete(*self.folder_tree.get_children())

        folders = {
            "Desktop":   "Desktop",
            "Personal":  "Documents",
            "MyPictures":"Pictures",
            "MyMusic":   "Music",
            "MyVideos":  "Videos",
            "{374DE290-123F-4565-9164-39C4925E467B}": "Downloads",
            "Favorites": "Favorites"
        }

        onedrive = os.environ.get("OneDrive", "")

        for reg_key, display_name in folders.items():
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders") as key:
                    raw = winreg.QueryValueEx(key, reg_key)[0]
                path = os.path.expandvars(raw)
                status = "NOT LOCAL" if (onedrive and path.startswith(onedrive)) else "LOCAL"
            except Exception:
                path, status = "", "UNKNOWN"

            self.folder_tree.insert("", "end", values=(display_name, status, path))

    def restore_shell_defaults(self):
        if not messagebox.askyesno("Confirm", "This will reset all special folders to local paths.\nProceed?"):
            return

        base = os.environ["USERPROFILE"]
        folders = {
            "Desktop":   "Desktop",
            "Personal":  "Documents",
            "MyPictures":"Pictures",
            "MyMusic":   "Music",
            "MyVideos":  "Videos",
            "{374DE290-123F-4565-9164-39C4925E467B}": "Downloads",
            "Favorites": "Favorites"
        }

        key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            for reg_name, folder_name in folders.items():
                target = os.path.join(base, folder_name)
                os.makedirs(target, exist_ok=True)
                try:
                    winreg.SetValueEx(key, reg_name, 0, winreg.REG_EXPAND_SZ, target)
                    if self.advanced_mode.get():
                        print(f"[DEBUG] Restored {reg_name} → {target}")
                except Exception as e:
                    print(f"[!] Failed to set {reg_name}: {e}")

        messagebox.showinfo("Done", "Shell folders restored to local defaults.\nExplorer will now refresh.")
        os.system("taskkill /f /im explorer.exe && start explorer.exe")
        self.refresh_shell_audit()

    # ── Monitor Methods ─────────────────────────────────────────────────────

    def refresh_monitor_info(self):
        self.monitor_tree.delete(*self.monitor_tree.get_children())

        try:
            monitors = win32api.EnumDisplayMonitors()
        except Exception as e:
            self.monitor_tree.insert("", "end", values=("Error", str(e), "", "", ""))
            return

        # Enable per-monitor DPI awareness for accurate readings
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            pass

        for idx, (hmon, _, rect) in enumerate(monitors, start=1):
            try:
                info    = win32api.GetMonitorInfo(hmon)
                mon_rect = info["Monitor"]          # (left, top, right, bottom) physical pixels
                flags   = info.get("Flags", 0)
                is_primary = "✔" if flags & 1 else ""

                left, top, right, bottom = mon_rect
                width  = right  - left
                height = bottom - top
                res    = f"{width} × {height}"
                pos    = f"{left}, {top}"

                # DPI scale via shcore
                try:
                    dpi_x = ctypes.c_uint()
                    dpi_y = ctypes.c_uint()
                    ctypes.windll.shcore.GetDpiForMonitor(
                        hmon.handle, 0, ctypes.byref(dpi_x), ctypes.byref(dpi_y)
                    )
                    scale = f"{round(dpi_x.value / 96 * 100)}%"
                except Exception:
                    scale = "N/A"

                self.monitor_tree.insert("", "end", values=(
                    f"Monitor {idx}", res, pos, scale, is_primary
                ))

                if self.advanced_mode.get():
                    print(f"[MONITOR {idx}] {res} @ ({pos}) DPI={scale} Primary={bool(flags & 1)}")

            except Exception as e:
                self.monitor_tree.insert("", "end", values=(f"Monitor {idx}", "Error", str(e), "", ""))