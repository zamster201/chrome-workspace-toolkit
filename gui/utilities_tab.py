# gui/utilities_tab.py

"""
UtilitiesTab – Chrome Workspace Toolkit (CWT)

Provides system-level tools such as shell folder audit and default mapping restore.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import winreg

# Tooltip replacement for Tkinter (safe version)
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)

    def on_enter(self, event=None):
        if self.tip_window or not self.text:
            return
        try:
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
            self.tip_window = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.geometry(f"+{x}+{y}")
            label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                            background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                            font=("tahoma", "8", "normal"))
            label.pack(ipadx=5, ipady=2)
        except:
            pass

    def on_leave(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class UtilitiesTab(ttk.Frame):
    def __init__(self, master, advanced_mode):
        self.advanced_mode = advanced_mode
        super().__init__(master)
        self.frame = tk.Frame(master)
        self._build_ui()

    def _build_ui(self):
        ttk.Label(self.frame, text="🧰 Shell Folder Audit & Remap", font=("Arial", 14)).pack(pady=(20, 10))

        self.adv_check = ttk.Checkbutton(self.frame, text="Advanced Mode", variable=self.advanced_mode)
        self.adv_check.pack(anchor="w", padx=10)

        self.folder_tree = ttk.Treeview(self.frame, columns=("Status", "Path"), show="headings", height=8)
        self.folder_tree.heading("Status", text="Status")
        self.folder_tree.heading("Path", text="Path")
        self.folder_tree.column("Status", width=100, anchor="center")
        self.folder_tree.column("Path", width=400)
        self.folder_tree.pack(pady=5)

        button_frame = tk.Frame(self.frame)
        button_frame.pack(pady=5)

        refresh_btn = ttk.Button(button_frame, text="🔄 Refresh Status", command=self.refresh_shell_audit)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(refresh_btn, "Re-scan current user shell folder paths")

        restore_btn = ttk.Button(button_frame, text="🚰 Restore Defaults", command=self.restore_shell_defaults)
        restore_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(restore_btn, "Restore system folder mappings to local user profile")

        self.refresh_shell_audit()

    def refresh_shell_audit(self):
        self.folder_tree.delete(*self.folder_tree.get_children())

        folders = {
            "Desktop": "Desktop",
            "Personal": "Documents",
            "MyPictures": "Pictures",
            "MyMusic": "Music",
            "MyVideos": "Videos",
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
                if not path:
                    status = "UNKNOWN"
                elif onedrive and path.startswith(onedrive):
                    status = "NOT LOCAL"
                else:
                    status = "LOCAL"
            except:
                path = ""
                status = "UNKNOWN"

            if self.advanced_mode.get():
                print(f"[DEBUG] {display_name}: {status} → {path}")

            self.folder_tree.insert("", "end", values=(display_name, status, path))

    def restore_shell_defaults(self):
        confirm = messagebox.askyesno("Confirm", "This will reset all special folders to local paths.\nProceed?")
        if not confirm:
            return

        base = os.environ["USERPROFILE"]
        folders = {
            "Desktop": "Desktop",
            "Personal": "Documents",
            "MyPictures": "Pictures",
            "MyMusic": "Music",
            "MyVideos": "Videos",
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
