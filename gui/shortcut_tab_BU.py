# gui/shortcut_tab.py

"""
ShortcutTab – Chrome Workspace Toolkit (CWT)

Generates Windows shortcuts (.lnk) for selected Chrome profiles.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
import os
import win32com.client
from utils.paths import get_desktop_path

# Tooltip replacement for Tkinter (cross-platform)
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        try:
            x, y, _, cy = self.widget.bbox("insert")
        except Exception:
            x = y = cy = 0
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + cy + 10
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                font=("tahoma", "8", "normal"))
        label.pack(ipadx=5, ipady=2)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class ShortcutTab:
    def __init__(self, master):
        self.frame = tk.Frame(master)
        self.chrome_path = self._detect_chrome()
        self.profile_root = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
        self.profiles = self._get_profiles()
        self._build_ui()

    def _detect_chrome(self):
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return "chrome.exe"

    def _get_profiles(self):
        entries = os.listdir(self.profile_root)
        profiles = []
        for name in entries:
            path = os.path.join(self.profile_root, name)
            prefs = os.path.join(path, "Preferences")

            if os.path.isdir(path) and os.path.isfile(prefs):
                if name != "System Profile":
                    profiles.append(name)
        return sorted(profiles)

    def _build_ui(self):

        tk.Label(self.frame, text="Create Shortcuts from these Profiles", font=("Arial", 14)).pack(pady=10)
        self.listbox = tk.Listbox(self.frame, selectmode=tk.EXTENDED, width=40, height=12)
        for profile in self.profiles:
            self.listbox.insert(tk.END, profile)
        self.listbox.pack(pady=5)
        ToolTip(self.listbox, "Ctrl or Shift to select multiple profiles")

        # Combo entry box for folder selection or creation
        tk.Label(self.frame, text="Target Folder for Shortcuts:").pack()
        self.folder_var = tk.StringVar()
        self.folder_combo = ttk.Combobox(self.frame, textvariable=self.folder_var)
        self.folder_combo['values'] = self._get_existing_workspace_folders()
        self.folder_combo.pack(pady=5)
        ToolTip(self.folder_combo, "Select existing folder or input a new name")

        generate_btn = tk.Button(self.frame, text="Create Shortcuts", command=self.create_shortcuts)
        generate_btn.pack(pady=10)
        ToolTip(generate_btn, "Generate .lnk shortcuts for selected Chrome profiles")

    def _get_existing_workspace_folders(self):
        base = Path(get_desktop_path()) / "CWT Shortcuts"
        if not base.exists():
            return []
        return [f.name for f in base.iterdir() if f.is_dir()]

    def create_shortcuts(self):
        indices = self.listbox.curselection()
        selected = [self.listbox.get(i) for i in indices]

        if not selected:
            messagebox.showwarning("No Profile selected", "Please select at least one profile.")
            return

        base_dir = Path(get_desktop_path()) / "CWT Shortcuts"
        target_folder = self.folder_var.get().strip()
        if not target_folder:
            messagebox.showwarning("No Folder selected", "Please select or enter a target folder.")
            return

        shortcut_dir = base_dir / target_folder
        shortcut_dir.mkdir(parents=True, exist_ok=True)

        shell = win32com.client.Dispatch("WScript.Shell")

        for profile in selected:
            shortcut_path = shortcut_dir / f"{profile}.lnk"
            profile_arg = f'--profile-directory="{profile}"'

            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = self.chrome_path
            shortcut.Arguments = profile_arg
            shortcut.WorkingDirectory = os.path.dirname(self.chrome_path)
            shortcut.IconLocation = self.chrome_path
            shortcut.save()

        messagebox.showinfo("Done", f"Created {len(selected)} shortcut(s) in:\n{shortcut_dir}")
