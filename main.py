# gui/main_window.py

"""
Module: main.py
Part of: Chrome Workspace Toolkit (CWT)

Description:
    Entry point for the CWT application. Initializes the main window and GUI tabs.

Author: Tom
Last Updated: 2025-04-13
"""

import tkinter as tk
from tkinter import ttk
from gui.shortcut_tab import ShortcutTab
from gui.utilities_tab import UtilitiesTab
from gui.workspace_tab import WorkspaceTab
from gui.profile_tab import ProfileTab
from gui.snapshot_tab import SnapshotTab

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.advanced_mode = tk.BooleanVar(master=self.root, value=False)
        self.root.title("Chrome Workspace Toolkit")
        self.root.geometry("680x620")

        style = ttk.Style()
        style.configure("TLabel", font=("Segoe UI Bold", 10))
        style.configure("TButton", font=("Segoe UI Semibold", 8))
        style.configure("TCheckbutton", font=("Segoe UI", 9))
        style.configure("Header.TLabel", font=("Segoe UI Semibold", 9))
        style.configure("Bold.TLabelframe.Label", font=("Segoe UI Semibold", 10))
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.workspace_tab = WorkspaceTab(self.notebook, advanced_mode=self.advanced_mode)
        self.shortcut_tab = ShortcutTab(self.notebook, advanced_mode=self.advanced_mode)
        self.snapshot_tab = SnapshotTab(self.notebook, advanced_mode=self.advanced_mode)
        self.profile_tab = ProfileTab(self.notebook, advanced_mode=self.advanced_mode)
        self.utilities_tab = UtilitiesTab(self.notebook, advanced_mode=self.advanced_mode)
        workspace_tab = WorkspaceTab(self.notebook, advanced_mode=self.advanced_mode)
        self.notebook.add(self.workspace_tab, text="Workspace")
        snapshot_tab = SnapshotTab(self.notebook, advanced_mode=self.advanced_mode)
        self.notebook.add(self.snapshot_tab, text="Snapshot")
        shortcut_tab = ShortcutTab(self.notebook, advanced_mode=self.advanced_mode)
        self.notebook.add(self.shortcut_tab, text="Shortcuts")
        profile_tab = ProfileTab(self.notebook, advanced_mode=self.advanced_mode)
        self.notebook.add(self.profile_tab, text="Profiles")
        utilities_tab = UtilitiesTab(self.notebook, advanced_mode=self.advanced_mode)
        self.notebook.add(self.utilities_tab, text="Utilities")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("520x400+700+700")                               # For Testing purposes
    app = MainWindow(root)
    root.mainloop()
