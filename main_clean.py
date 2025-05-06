
import tkinter as tk
from tkinter import ttk

from gui.workspace_tab import WorkspaceTab
from gui.snapshot_tab import SnapshotTab
from gui.shortcut_tab import ShortcutTab
from gui.profile_tab import ProfileTab
from gui.utilities_tab import UtilitiesTab

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Chrome Workspace Toolkit")
        self.root.geometry("680x620")
        self.advanced_mode = tk.BooleanVar(master=self.root, value=False)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.workspace_tab = WorkspaceTab(self.notebook, advanced_mode=self.advanced_mode)
        self.snapshot_tab = SnapshotTab(self.notebook, advanced_mode=self.advanced_mode)
        self.shortcut_tab = ShortcutTab(self.notebook, advanced_mode=self.advanced_mode)
        self.profile_tab = ProfileTab(self.notebook, advanced_mode=self.advanced_mode)
        self.utilities_tab = UtilitiesTab(self.notebook, advanced_mode=self.advanced_mode)

        self.notebook.add(self.workspace_tab, text="Workspace")
        self.notebook.add(self.snapshot_tab, text="Snapshot")
        self.notebook.add(self.shortcut_tab, text="Shortcuts")
        self.notebook.add(self.profile_tab, text="Profiles")
        self.notebook.add(self.utilities_tab, text="Utilities")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
