
import tkinter as tk
from tkinter import ttk
from gui.workspace_tab import WorkspaceTab
from gui.snapshot_tab import SnapshotTab
from gui.shortcut_tab import ShortcutTab
from gui.profile_tab import ProfileTab
from gui.utilities_tab import UtilitiesTab

def construct_gui(active_tab):
    root = tk.Tk()
    root.geometry("680x620")
    root.title(f"Stepwise Main Debug: {active_tab}")

    advanced_mode = tk.BooleanVar(master=root, value=False)
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    tab_map = {
        "Workspace": lambda: WorkspaceTab(notebook, advanced_mode),
        "Snapshot": lambda: SnapshotTab(notebook, advanced_mode),
        "Shortcuts": lambda: ShortcutTab(notebook, advanced_mode),
        "Profiles": lambda: ProfileTab(notebook, advanced_mode),
        "Utilities": lambda: UtilitiesTab(notebook, advanced_mode),
    }

    if active_tab in tab_map:
        print(f"🧪 Constructing: {active_tab}")
        try:
            tab = tab_map[active_tab]()
            notebook.add(tab, text=active_tab)
        except Exception as e:
            print(f"❌ Error constructing {active_tab}: {e}")

    root.mainloop()

if __name__ == "__main__":
    # Change this line to test different tabs
    construct_gui("Utilities")
