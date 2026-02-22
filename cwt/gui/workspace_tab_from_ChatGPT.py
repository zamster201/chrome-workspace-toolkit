# gui/workspace_tab.py

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import json
from datetime import datetime

class WorkspaceTab(ttk.Frame):
    def __init__(self, master, advanced_mode):
        self.advanced_mode = advanced_mode
        super().__init__(master)
        self.workspace_dir = Path("storage/workspaces")
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self._build_ui()

    def _build_ui(self):
        self.config(width=680)

        style = ttk.Style()
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("TCheckbutton", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI Semibold", 10))

        # --- Save Workspace Section ---
        save_frame = ttk.LabelFrame(self, text="Create Workspace")
        save_frame.pack(fill="x", padx=10, pady=(10, 5))

        save_row = ttk.Frame(save_frame)
        save_row.pack(fill="x", padx=(20, 5), pady=(5, 0))

        ttk.Label(save_row, text="Workspace Name:", style="Header.TLabel").pack(side="left")
        self.name_var = tk.StringVar()
        self.name_combo = ttk.Combobox(save_row, textvariable=self.name_var, width=25)
        self.name_combo.pack(side="left", padx=(5, 5))

        self.save_button = ttk.Button(save_row, text="Create Workspace", command=self._save_workspace)
        self.save_button.pack(side="left")

        hint1 = ttk.Label(save_frame, text="[ Default Name : WS.DD-MMM-YY_HHMM ]", font=("Segoe UI", 8))
        hint1.pack(anchor="w", padx=(145, 5), pady=(0, 2))

        self.capture_only = tk.BooleanVar()
        ttk.Checkbutton(
            save_frame,
            text="Capture Snapshot Only (Workspace metadata is NOT captured)",
            variable=self.capture_only
        ).pack(anchor="w", padx=(20, 5), pady=(2, 5))

        # --- Divider ---
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=10, pady=10)

        # --- Restore Workspace Section ---
        restore_frame = ttk.LabelFrame(self, text="Restore Workspace")
        restore_frame.pack(fill="x", padx=10, pady=(0, 10))

        restore_row = ttk.Frame(restore_frame)
        restore_row.pack(fill="x", padx=(20, 5), pady=(5, 0))

        ttk.Label(restore_row, text="Workspace Name:", style="Header.TLabel").pack(side="left")
        self.restore_dropdown = ttk.Combobox(restore_row, state="readonly", width=25)
        self.restore_dropdown.pack(side="left", padx=(5, 5))
        self.restore_dropdown.bind("<<ComboboxSelected>>", self._load_workspace)

        self.restore_button = ttk.Button(restore_row, text="Restore Workspace", command=self._restore_workspace)
        self.restore_button.pack(side="left")

        hint2 = ttk.Label(restore_frame, text="[ Select a Workspace ]", font=("Segoe UI", 8))
        hint2.pack(anchor="w", padx=(150, 5), pady=(0, 5))

        option_row = ttk.Frame(restore_frame)
        option_row.pack(fill="x", padx=(20, 5), pady=(5, 5))

        self.restore_apps = tk.BooleanVar()
        self.restore_schema = tk.BooleanVar()
        ttk.Checkbutton(option_row, text="Restore Applications", variable=self.restore_apps).pack(side="left")
        ttk.Checkbutton(option_row, text="Restore Desktop Schema", variable=self.restore_schema).pack(side="left", padx=10)

        # --- Advanced Mode Toggle ---
        adv_frame = ttk.Frame(self)
        adv_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        ttk.Checkbutton(adv_frame, text="Advanced Mode", variable=self.advanced_mode).pack(anchor="e")

        self.log_output = tk.Text(adv_frame, height=8, wrap="word")
        if self.advanced_mode.get():
            self.log_output.pack(fill="both", expand=True)

    def _save_workspace(self):
        name = self.name_var.get().strip()
        if not name:
            name = "WS." + datetime.now().strftime("%d-%b-%y_%H%M")

        if self.capture_only.get():
            from cwt.core.snapshot_capture import capture_snapshot
            capture_snapshot(workspace_name=name)
            messagebox.showinfo("Snapshot Captured", f"Snapshot captured under '{name}'")
            return

        data = {
            "workspace": name,
            "desktops": {},
            "snapshots": []
        }

        path = self.workspace_dir / f"{name}.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        self._refresh_workspace_list()
        messagebox.showinfo("Workspace Saved", f"Workspace '{name}' has been created.")

    def _load_workspace(self, event):
        selected = self.restore_dropdown.get()
        if not selected:
            return
        print(f"[DEBUG] Loaded workspace: {selected}")

    def _restore_workspace(self):
        selected = self.restore_dropdown.get()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a workspace to restore.")
            return
        restore_apps = self.restore_apps.get()
        restore_schema = self.restore_schema.get()
        print(f"[DEBUG] Restoring '{selected}' ? Apps: {restore_apps}, Schema: {restore_schema}")

    def _refresh_workspace_list(self):
        files = list(self.workspace_dir.glob("*.json"))
        names = [f.stem for f in files]
        self.restore_dropdown["values"] = names
        self.name_combo["values"] = names
