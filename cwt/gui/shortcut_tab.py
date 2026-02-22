import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess

from cwt.utils.tooltip import ToolTip


class ShortcutTab(ttk.Frame):
    def __init__(self, master, advanced_mode):
        super().__init__(master)
        self.advanced_mode = advanced_mode
        self.chrome_path = self._detect_chrome()
        self.profile_root = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
        self.profiles = self._get_profiles()
        self.target_dir = tk.StringVar(master=self,value=os.path.join(os.environ["USERPROFILE"], "Desktop"))
        self._build_ui()

    def _build_ui(self):
        header = ttk.Label(self, text="Create Shortcuts from these Profiles", font=("Segoe UI", 12, "bold"))
        header.pack(pady=(20, 0))

        self.adv_check = ttk.Checkbutton(self, text="Advanced Mode", variable=self.advanced_mode)
        self.adv_check.pack(anchor="ne", padx=20, pady=(15, 0))
        ToolTip(self.adv_check, "Enable internal logging and diagnostic output.")

        list_row = ttk.Frame(self)
        list_row.pack(padx=15, pady=10, fill="x")

        self.listbox = tk.Listbox(list_row, selectmode=tk.EXTENDED, width=40, height=10)
        self.listbox.pack()
        ToolTip(self.listbox, "Ctrl or Shift to select multiple profiles.")

        folder_row = ttk.Frame(self)
        folder_row.pack(fill="x", padx=30, pady=(25, 0))

        ttk.Label(folder_row, text="Shortcut Target Folder:").pack(side="left")

        folder_entry = ttk.Entry(folder_row, textvariable=self.target_dir, width=40)
        folder_entry.pack(side="left", padx=40)
        ToolTip(folder_entry, "Folder where .lnk files will be created.")

        browse_btn = ttk.Button(folder_row, text="Browse", command=self._browse_folder)
        browse_btn.pack(side="left")
        ToolTip(browse_btn, "Select a different folder for shortcut output.")

        gen_btn = ttk.Button(self, text="🚀 Generate Shortcuts", command=self._generate_shortcuts)
        gen_btn.pack(pady=30)
        ToolTip(gen_btn, "Create .lnk files for selected Chrome profiles in the target folder.")

        self.status_label = ttk.Label(self, text="", foreground="gray")
        self.status_label.pack(pady=(5, 0))

    def _detect_chrome(self):
        default_path = os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe")
        return default_path if os.path.exists(default_path) else "chrome.exe"

    def _get_profiles(self):
        try:
            return [
                d for d in os.listdir(self.profile_root)
                if os.path.isdir(os.path.join(self.profile_root, d)) and d.startswith("Profile")
            ]
        except Exception:
            return []

    def _browse_folder(self):
        folder = filedialog.askdirectory(title="Select Shortcut Output Folder")
        if folder:
            self.target_dir.set(folder)

    def _generate_shortcuts(self):
        selections = [self.listbox.get(i) for i in self.listbox.curselection()]
        if not selections:
            messagebox.showwarning("No Profiles Selected", "Please select at least one profile.")
            return

        target = self.target_dir.get()
        if not os.path.isdir(target):
            messagebox.showerror("Invalid Folder", f"Target folder does not exist:\n{target}")
            return

        for profile in selections:
            shortcut_name = f"Chrome - {profile}.lnk"
            shortcut_path = os.path.join(target, shortcut_name)

            cmd = [
                "powershell", "-Command",
                f"$s=(New-Object -COM WScript.Shell).CreateShortcut('{shortcut_path}');"
                f"$s.TargetPath='{self.chrome_path}';"
                f"$s.Arguments='--profile-directory=\"{profile}\"';"
                f"$s.IconLocation='{self.chrome_path},0';"
                "$s.Save()"
            ]

            try:
                subprocess.run(cmd, check=True)
                if self.advanced_mode.get():
                    print(f"[✓] Shortcut created: {shortcut_path}")
            except subprocess.CalledProcessError:
                print(f"[!] Failed to create shortcut for {profile}")
                messagebox.showerror("Error", f"Failed to create shortcut for: {profile}")

        self.status_label.config(text=f"[✓] {len(selections)} shortcut(s) created in {target}")
