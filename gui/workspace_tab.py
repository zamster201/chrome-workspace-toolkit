# gui/workspace_tab.py

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import json
from utils.tooltip import ToolTip
from datetime import datetime

class WorkspaceTab(ttk.Frame):
    def __init__(self, master, advanced_mode):
        super().__init__(master)
        self.advanced_mode = advanced_mode
        self.workspace_dir = Path("storage/workspaces")
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self._build_ui()

    def _build_ui(self):
        self.config(width=680)
        header = ttk.Label(self, text="Workspace Management", font=("Segoe UI", 12, "bold"))
        header.pack(pady=(10, 0))

        self.adv_check = ttk.Checkbutton(self, text="Advanced Mode", variable=self.advanced_mode)
        self.adv_check.pack(anchor="ne", padx=20, pady=(5, 0))
        ToolTip(self.adv_check, "Enable debug output and display Workspace metadata")

        # --- Save Workspace Section ---
        save_frame = ttk.LabelFrame(self, text="  Create Workspace  ", style="Bold.TLabelframe")
        save_frame.pack(fill="x", padx=20, pady=(10,7))  ####

        save_row = ttk.Frame(save_frame)
        save_row.pack(fill="x", padx=(10, 10), pady=(5, 5))

        ttk.Label(save_row, text="Workspace Name:", style="Header.TLabel").pack(side="left", padx=(12, 4))
        self.name_var = tk.StringVar(master=self)
        self.name_combo = ttk.Combobox(save_row, textvariable=self.name_var, width=30)
        self.name_combo.pack(side="left", padx=(5, 10))
        ToolTip(self.name_combo, "Enter a name to identify this workspace layout")

        hint1 = ttk.Label(save_frame, text="[ Default Name : WS.DD-MMM-YY_HHMM ]", font=("Segoe UI", 8))
        hint1.pack(anchor="w", padx=(127, 10), pady=(2, 10))

        self.save_button = ttk.Button(save_row, text=" 📸 Create Workspace ", command=self._save_workspace)
        self.save_button.pack(side="left")
        ToolTip(self.save_button, "Capture the current window arrangement and save it under this workspace")

        self.capture_only = tk.BooleanVar(master=self)
        ttk.Checkbutton(
            save_frame,
            text="Capture Workspace metadata ONLY",
            variable=self.capture_only
        ).pack(anchor="w", padx=(24, 5), pady=(10, 10))


        # --- Divider ---

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=20, pady=10)  ###

        # --- Restore Workspace Section ---
        restore_frame = ttk.LabelFrame(self, text="  Restore Workspace  ", style="Bold.TLabelframe")
        restore_frame.pack(fill="x", padx=20, pady=(0, 0))

        restore_row = ttk.Frame(restore_frame)
        restore_row.pack(fill="x", padx=(10, 10), pady=(5, 7))  # was 5

        ttk.Label(restore_row, text="Workspace Name:", style="Header.TLabel").pack(side="left", padx=(12, 5))
        self.restore_dropdown = ttk.Combobox(restore_row, state="readonly", width=30)
        self.restore_dropdown.pack(side="left", padx=(5, 10)) ##
        self.restore_dropdown.bind("<<ComboboxSelected>>", self._load_workspace)

        self.restore_button = ttk.Button(restore_row, text="🧩 Restore Workspace ", command=self._restore_workspace)
        self.restore_button.pack(side="left")
        ToolTip(self.restore_button, "Restore windows to their saved positions based on the selected workspace")

        hint2 = ttk.Label(restore_frame, text="[ Select a Workspace ]", font=("Segoe UI", 8))
        hint2.pack(anchor="w", padx=(178, 5), pady=(1, 5))

        option_row = ttk.Frame(restore_frame)
        option_row.pack(fill="x", padx=(20, 5), pady=(12, 10))

        self.restore_apps = tk.BooleanVar(master=self)
        self.restore_schema = tk.BooleanVar(master=self)
        ttk.Checkbutton(option_row, text="Restore Applications", variable=self.restore_apps).pack(side="left",padx=(3,0))

        ttk.Checkbutton(option_row, text="Restore Desktop Schema", variable=self.restore_schema).pack(side="left", padx=10)

    def _save_workspace(self):
        name = self.name_var.get().strip()
        if not name:
            name = "WS." + datetime.now().strftime("%d-%b-%y_%H%M")

        if self.capture_only.get():
            from core.snapshot_capture import capture_snapshot
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
        messagebox.showinfo("Workspace Saved", f"Workspace '{name}' has been created")

    def _load_workspace(self, event):
        selected = self.restore_dropdown.get()
        if not selected:
            return
        print(f"[DEBUG] Loaded workspace: {selected}")

    def _restore_workspace(self):
        selected = self.restore_dropdown.get()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a workspace to restore")
            return
        restore_apps = self.restore_apps.get()
        restore_schema = self.restore_schema.get()
        print(f"[DEBUG] Restoring '{selected}' → Apps: {restore_apps}, Schema: {restore_schema}")

    def _refresh_workspace_list(self):
        files = list(self.workspace_dir.glob("*.json"))
        names = [f.stem for f in files]
        self.restore_dropdown["values"] = names
        self.name_combo["values"] = names

        self.meta_frame = ttk.LabelFrame(self, text="Workspace Metadata", style="Bold.TLabelframe")
        self.meta_frame.pack(fill="x", padx=20, pady=(0, 10))
        self.meta_labels = {}
        ToolTip(self.meta_frame, "Snapshot metadata shown here when Advanced Mode is enabled")

        for key in ["desktop_count", "desktop_names", "snapshot_count"]:
            row = ttk.Frame(self.meta_frame)
            row.pack(fill="x", padx=5, pady=1)
            label = ttk.Label(row, text=f"{key.replace('_', ' ').title()}:", width=16, anchor="w")
            label.pack(side="left")
            value = ttk.Label(row, text="", anchor="w")
            value.pack(side="left", fill="x", expand=True)
            self.meta_labels[key] = value
