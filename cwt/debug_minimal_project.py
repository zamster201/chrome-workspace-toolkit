from pathlib import Path

# Rewriting debug_minimal_project.py after session reset

import tkinter as tk
from tkinter import ttk
from cwt.gui.workspace_tab import WorkspaceTab
from cwt.gui.snapshot_tab import SnapshotTab
from cwt.gui.shortcut_tab import ShortcutTab
from cwt.gui.profile_tab import ProfileTab
from cwt.gui.utilities_tab import UtilitiesTab
import gc

root = tk.Tk()
root.geometry("600x400")
root.title("Debug: Minimal Project")

advanced_mode = tk.BooleanVar(master=root, value=False)
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Map of tab name -> constructor
tabs = {
    "Workspace": lambda: WorkspaceTab(notebook, advanced_mode=advanced_mode),
    "Snapshot": lambda: SnapshotTab(notebook, advanced_mode=advanced_mode),
    "Shortcuts": lambda: ShortcutTab(notebook, advanced_mode=advanced_mode),
    "Profiles": lambda: ProfileTab(notebook, advanced_mode=advanced_mode),
    "Utilities": lambda: UtilitiesTab(notebook, advanced_mode=advanced_mode),
}

tab_keys = list(tabs.keys())
constructed = []

def scan_tk_roots():
    print("xxx SCANNING: Active tk.Tk() instances in memory:")
    for obj in gc.get_objects():
        try:
            if isinstance(obj, tk.Tk):
                print("  ↪", obj, "Title:", obj.title())
        except Exception:
            pass

def construct_next_tab():
    if not tab_keys:
        print("xxx All tabs constructed.")
        scan_tk_roots()
        return

    tab_name = tab_keys.pop(0)
    print(f"xxx  Constructing tab: {tab_name}")
    try:
        tab = tabs[tab_name]()
        notebook.add(tab, text=tab_name)
        constructed.append(tab)
    except Exception as e:
        print(f"xxx Failed to construct {tab_name}: {e}")

    root.after(1000, construct_next_tab)

root.after(500, construct_next_tab)
root.mainloop()


