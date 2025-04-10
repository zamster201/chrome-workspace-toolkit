# Snapshot Tab - Chrome Workspace Toolkit (CWT)

import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
from core.snapshot_capture import capture_snapshot
from core.restore import restore_windows

class SnapshotTab:
    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text="Snapshots")
        self._build_ui()

    def _build_ui(self):
        custom_font = ("Courier New", 10)

        # --- Workspace Folder Selector (Moved and Renamed) ---
        name_frame = ttk.Frame(self.frame)
        name_frame.pack(pady=(10, 5))

        ttk.Label(name_frame, text="Workspace Name:").pack(side=tk.LEFT, padx=(0, 5))
        self.folder_var = tk.StringVar()
        self.folder_combo = ttk.Combobox(name_frame, textvariable=self.folder_var)
        self.folder_combo['values'] = self._get_existing_workspace_folders()
        self.folder_combo.pack(side=tk.LEFT)
        self.folder_combo.bind("<<ComboboxSelected>>", self._check_workspace_selection)
        self.folder_var.trace_add("write", lambda *_: self._check_workspace_selection())

        ttk.Label(self.frame, text="This name groups related snapshots", foreground="gray").pack()

        # --- Snapshot Selector ---
        selector_frame = ttk.Frame(self.frame)
        selector_frame.pack(pady=(10, 5))

        ttk.Label(selector_frame, text="Workspace:").pack(side=tk.LEFT, padx=(0, 5))
        self.workspace_dropdown = ttk.Combobox(selector_frame, state="readonly")
        self.workspace_dropdown.pack(side=tk.LEFT)
        self.workspace_dropdown.bind("<<ComboboxSelected>>", self.update_snapshot_dropdown)

        ttk.Label(selector_frame, text="Snapshot:").pack(side=tk.LEFT, padx=(10, 5))
        self.snapshot_dropdown = ttk.Combobox(selector_frame, state="readonly")
        self.snapshot_dropdown.pack(side=tk.LEFT)
        self.snapshot_dropdown.bind("<<ComboboxSelected>>", self._check_snapshot_selection)

        ttk.Label(self.frame, text="Select workspace & snapshot to restore", foreground="gray").pack()

        # --- Multi-Select Tip ---
        ttk.Label(self.frame, text="Tip: Ctrl or Shift to multi-select (where supported)", foreground="gray").pack(pady=(2, 0))

        # --- Buttons ---
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(pady=10)

        self.restore_btn = ttk.Button(button_frame, text="🗀 Restore Snapshot", command=self.handle_restore)
        self.restore_btn.pack(side=tk.LEFT, padx=10)

        self.capture_btn = ttk.Button(button_frame, text="📸 Capture Snapshot", command=self.handle_capture)
        self.capture_btn.pack(side=tk.LEFT, padx=10)

        # --- Debug Output Box ---
        ttk.Label(self.frame, text="Debug Output").pack(anchor="w", padx=10)
        self.debug_box = tk.Text(self.frame, height=8, bg="black", fg="lightgreen", font=custom_font)
        self.debug_box.pack(fill="both", expand=False, padx=10, pady=(0, 10))

        self.populate_workspace_dropdown()

    def _get_existing_workspace_folders(self):
        snapshot_root = Path("snapshots")
        if not snapshot_root.exists():
            snapshot_root.mkdir()
        return [f.name for f in snapshot_root.iterdir() if f.is_dir()]

    def log(self, msg):
        self.debug_box.insert(tk.END, msg + "\n")
        self.debug_box.see(tk.END)

    def populate_workspace_dropdown(self):
        snapshot_root = Path("snapshots")
        if not snapshot_root.exists():
            snapshot_root.mkdir()
        workspaces = [d.name for d in snapshot_root.iterdir() if d.is_dir()]
        self.workspace_dropdown["values"] = workspaces

    def update_snapshot_dropdown(self, event=None):
        selected_workspace = self.workspace_dropdown.get()
        snapshot_root = Path("snapshots") / selected_workspace
        snapshots = [f.name for f in snapshot_root.glob("*.json")]
        self.snapshot_dropdown["values"] = sorted(snapshots, reverse=True)
        self._check_snapshot_selection()

    def _check_workspace_selection(self, *args):
        if self.folder_var.get():
            self.capture_btn.state(["!disabled"])
        else:
            self.capture_btn.state(["disabled"])

    def _check_snapshot_selection(self, event=None):
        if self.snapshot_dropdown.get():
            self.capture_btn.state(["disabled"])
        elif self.folder_var.get():
            self.capture_btn.state(["!disabled"])

    def handle_capture(self):
        workspace_name = self.folder_var.get() or "Unnamed Workspace"
        capture_snapshot(workspace_name=workspace_name, logger=self.log)
        self.populate_workspace_dropdown()

    def handle_restore(self):
        workspace = self.workspace_dropdown.get()
        snap = self.snapshot_dropdown.get()
        if workspace and snap:
            snapshot_path = Path("snapshots") / workspace / snap
            restore_windows(snapshot_path, logger=self.log)
