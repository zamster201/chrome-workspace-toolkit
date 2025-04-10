"""
Module: profile_tab.py
Part of: Chrome Workspace Toolkit (CWT)

Description:
    UI and logic for managing Chrome profiles. Dynamically detects available
    Chrome profiles from the user data directory and supports launching
    multiple profiles at once via a listbox.

Author: Tom
Last Updated: 2025-03-31
"""

import tkinter as tk
import subprocess
import os
from pathlib import Path
import json

class ProfileTab:
    def __init__(self, master):
        self.frame = tk.Frame(master)
        self.chrome_path = self._detect_chrome()
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
        profile_root = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
        if not os.path.exists(profile_root):
            return []

        known_garbage = {
            "Crashpad", "System Profile", "Crowd Deny", "Safe Browsing",
            "Webstore Downloads", "Subresource Filter", "Local Traces"
        }

        entries = os.listdir(profile_root)
        profiles = []

        for name in entries:
            path = os.path.join(profile_root, name)
            prefs_path = os.path.join(path, "Preferences")

            if not os.path.isdir(path):
                continue
            if name in known_garbage:
                continue
            if os.path.exists(prefs_path):
                profiles.append(name)

        return sorted(profiles)


    def refresh_profiles(self):
        self.profiles = self._get_profiles()
        self.listbox.delete(0, tk.END)
        for profile in self.profiles:
            self.listbox.insert(tk.END, profile)
        print("[✓] Profile list refreshed.")

    def launch_selected_profiles(self):
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            print("No profiles selected.")
            return

        for i in selected_indices:
            profile = self.listbox.get(i)
            try:
                subprocess.Popen([self.chrome_path, f'--profile-directory={profile}'])
                print(f"Launched: {profile}")
            except Exception as e:
                print(f"Error launching {profile}: {e}")

    def enable_restore_tabs(self):
        profile_root = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
        selected_indices = self.listbox.curselection()
        selected_profiles = [self.listbox.get(i) for i in selected_indices]
        patched = []

        for profile in selected_profiles:
            prefs_path = Path(profile_root) / profile / "Preferences"
            if not prefs_path.exists():
                continue

            try:
                # Backup
                backup_path = prefs_path.with_suffix(".bak")
                prefs_path.replace(backup_path)

                with backup_path.open("r", encoding="utf-8") as f:
                    prefs = json.load(f)

                prefs.setdefault("session", {})
                prefs["session"]["restore_on_startup"] = 1

                with prefs_path.open("w", encoding="utf-8") as f:
                    json.dump(prefs, f, indent=2)

                patched.append(profile)

            except Exception as e:
                print(f"[!] Failed to patch {profile}: {e}")

        msg = f"[✓] Patched {len(patched)} profiles:\n" + ", ".join(patched)
        print(msg)

    def _build_ui(self):
        label = tk.Label(self.frame, text="Chrome Profile Launcher", font=("Arial", 14))
        label.pack(pady=10)

        self.listbox = tk.Listbox(self.frame, selectmode=tk.EXTENDED, height=12, width=35)
        for profile in self.profiles:
            self.listbox.insert(tk.END, profile)
        self.listbox.pack(pady=5)

        launch_btn = tk.Button(self.frame, text="Launch Selected", command=self.launch_selected_profiles)
        launch_btn.pack(pady=5)

        # Restore Tabs patch button
        patch_btn = tk.Button(self.frame, text="Enable Restore Tabs", command=self.enable_restore_tabs)
        patch_btn.pack(pady=5)

