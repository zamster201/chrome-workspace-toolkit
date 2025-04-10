"""
Module: main_window.py
Part of: Chrome Workspace Toolkit (CWT)

Description:
    Builds the main GUI window for CWT. Includes a tabbed interface for
    Profiles, Shortcuts, Snapshots, and Sessions. Each tab is imported from
    its respective module and wired into a unified layout.

Author: Tom
Last Updated: 2025-03-31
"""

import tkinter as tk
from tkinter import ttk
from utils.debug_logger import set_log_callback

from gui.profile_tab import ProfileTab
from gui.shortcut_tab import ShortcutTab
from gui.snapshot_tab import SnapshotTab
from gui.session_tab import SessionTab
from gui.utilities_tab import UtilitiesTab

class MainWindow:
    def __init__(self, root):
        self.root = root
        root.title("Chrome Workspace Toolkit")
       # Center the window on the screen
        width, height = 600, 500
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")
        root.resizable(False, False)

        # Container frame for notebook + footer
        self.main_container = tk.Frame(root)
        self.main_container.pack(fill="both", expand=True)

        # Tabbed notebook
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        # Tabs
        self.profile_tab = ProfileTab(self.notebook)
        self.notebook.add(self.profile_tab.frame, text="Profiles")

        self.shortcut_tab = ShortcutTab(self.notebook)
        self.notebook.add(self.shortcut_tab.frame, text="Shortcuts")

        self.snapshot_tab = SnapshotTab(self.notebook)
        self.notebook.add(self.snapshot_tab.frame, text="Snapshots")

        self.utilities_tab = UtilitiesTab(self.notebook)
        self.notebook.add(self.utilities_tab.frame, text="Utilities")

        # Global Exit button
        exit_frame = tk.Frame(self.main_container)
        exit_frame.pack(fill="x", pady=(5, 10), padx=10, anchor="w")

        ttk.Button(exit_frame, text="⏹ Exit", command=root.quit).pack(side=tk.LEFT)
         # Debug Output Box
        # 1. Create the debug output widget (attach to main container for layout consistency)

        self.debug_output = tk.Text(self.main_container, height=8, bg="black", fg="white")
        self.debug_output.pack(fill=tk.X, padx=10, pady=(5, 0))

        # 2. Wire log output to debug window

        def log_to_debug_window(msg):
            self.debug_output.configure(state="normal")
            self.debug_output.insert("end", msg + "\n")
            self.debug_output.configure(state="disabled")
            self.debug_output.yview_moveto(1)

        set_log_callback(log_to_debug_window)
