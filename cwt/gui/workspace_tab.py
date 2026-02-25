# gui/workspace_tab.py

import uuid
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import json
from cwt.utils.tooltip import ToolTip
from cwt.utils.paths import get_workspaces_dir
from cwt.utils.vda_utils import get_virtual_desktop_id_map
from datetime import datetime

class WorkspaceTab(ttk.Frame):
    def __init__(self, master, advanced_mode):
        super().__init__(master)
        self.advanced_mode = advanced_mode
        self.workspace_dir = get_workspaces_dir()
        self._build_ui()
        self._refresh_workspace_list()

    def _build_ui(self):
        self.config(width=680)
        header = ttk.Label(self, text="Workspace Management", font=("Segoe UI", 12, "bold"))
        header.pack(pady=(10, 0))

        self.adv_check = ttk.Checkbutton(self, text="Advanced Mode", variable=self.advanced_mode)
        self.adv_check.pack(anchor="ne", padx=20, pady=(5, 0))
        ToolTip(self.adv_check, "Enable debug output and display Workspace metadata")

        # --- Create Workspace Section ---
        save_frame = ttk.LabelFrame(self, text="  Create Workspace  ", style="Bold.TLabelframe")
        save_frame.pack(fill="x", padx=20, pady=(10, 7))

        save_row = ttk.Frame(save_frame)
        save_row.pack(fill="x", padx=(10, 10), pady=(5, 5))

        ttk.Label(save_row, text="Workspace Name:", style="Header.TLabel").pack(side="left", padx=(12, 4))
        self.name_var = tk.StringVar(master=self)
        self.name_combo = ttk.Combobox(save_row, textvariable=self.name_var, width=30)
        self.name_combo.pack(side="left", padx=(5, 10))
        ToolTip(self.name_combo, "Enter a name to identify this workspace")

        ttk.Label(save_frame, text="[ Default Name : WS.DD-MMM-YY_HHMM ]", font=("Segoe UI", 8)).pack(
            anchor="w", padx=(127, 10), pady=(2, 10))

        self.save_button = ttk.Button(save_row, text=" 📸 Create Workspace ", command=self._save_workspace)
        self.save_button.pack(side="left")
        ToolTip(self.save_button, "Save current desktop layout as a new workspace definition")

        self.capture_only = tk.BooleanVar(master=self)
        ttk.Checkbutton(
            save_frame,
            text="Capture Workspace metadata ONLY (no snapshot)",
            variable=self.capture_only
        ).pack(anchor="w", padx=(24, 5), pady=(10, 10))

        # --- Divider ---
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=20, pady=10)

        # --- Restore Workspace Section ---
        restore_frame = ttk.LabelFrame(self, text="  Restore Workspace  ", style="Bold.TLabelframe")
        restore_frame.pack(fill="x", padx=20, pady=(0, 0))

        restore_row = ttk.Frame(restore_frame)
        restore_row.pack(fill="x", padx=(10, 10), pady=(5, 7))

        ttk.Label(restore_row, text="Workspace Name:", style="Header.TLabel").pack(side="left", padx=(12, 5))
        self.restore_dropdown = ttk.Combobox(restore_row, state="readonly", width=30)
        self.restore_dropdown.pack(side="left", padx=(5, 10))
        self.restore_dropdown.bind("<<ComboboxSelected>>", self._load_workspace)

        self.restore_button = ttk.Button(restore_row, text="🧩 Restore Workspace ", command=self._restore_workspace)
        self.restore_button.pack(side="left")
        ToolTip(self.restore_button, "Restore windows to their saved positions based on the selected workspace")

        ttk.Label(restore_frame, text="[ Select a Workspace ]", font=("Segoe UI", 8)).pack(
            anchor="w", padx=(178, 5), pady=(1, 5))

        option_row = ttk.Frame(restore_frame)
        option_row.pack(fill="x", padx=(20, 5), pady=(12, 10))

        self.restore_apps = tk.BooleanVar(master=self)
        self.restore_schema = tk.BooleanVar(master=self)
        ttk.Checkbutton(option_row, text="Restore Applications", variable=self.restore_apps).pack(side="left", padx=(3, 0))
        ttk.Checkbutton(option_row, text="Restore Desktop Schema", variable=self.restore_schema).pack(side="left", padx=10)

        # --- Metadata Section ---
        self.meta_frame = ttk.LabelFrame(self, text="Workspace Metadata", style="Bold.TLabelframe")
        self.meta_frame.pack(fill="x", padx=20, pady=(10, 10))
        self.meta_labels = {}

        for key in ["workspace_id", "created_at", "desktop_count", "desktop_names", "collection_count"]:
            row = ttk.Frame(self.meta_frame)
            row.pack(fill="x", padx=5, pady=1)
            ttk.Label(row, text=f"{key.replace('_', ' ').title()}:", width=16, anchor="w").pack(side="left")
            value = ttk.Label(row, text="—", anchor="w", foreground="#555")
            value.pack(side="left", fill="x", expand=True)
            self.meta_labels[key] = value

    def _save_workspace(self):
        name = self.name_var.get().strip()
        if not name:
            name = "WS." + datetime.now().strftime("%d-%b-%Y_%H%M")
            self.name_var.set(name)

        path = self.workspace_dir / f"{name}.json"
        if path.exists():
            if not messagebox.askyesno("Exists", f"Workspace '{name}' already exists. Overwrite?"):
                return

        # Capture live desktop layout
        desktop_map = get_virtual_desktop_id_map()
        workspace_id = str(uuid.uuid4())
        created_at = datetime.now().strftime("%d-%b-%Y %H:%M")

        data = {
            "format_version": "1.0",
            "workspace_name": name,
            "workspace_id": workspace_id,
            "created_at": created_at,
            "desktops": {str(k): v for k, v in desktop_map.items()},
            "collections": []
        }

        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        if not self.capture_only.get():
            # Also trigger a snapshot collection under the same name
            from cwt.core.snapshot_capture import capture_snapshot
            capture_snapshot(collection_name=name)
            data["collections"].append(name)

        self._refresh_workspace_list()
        self._show_metadata(data)
        messagebox.showinfo("Workspace Created", f"Workspace '{name}' has been saved.")

    def _load_workspace(self, event):
        selected = self.restore_dropdown.get()
        if not selected:
            return
        path = self.workspace_dir / f"{selected}.json"
        if not path.exists():
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._show_metadata(data)

    def _show_metadata(self, data: dict):
        desktops = data.get("desktops", {})
        mapping = {
            "workspace_id":    data.get("workspace_id", "—"),
            "created_at":      data.get("created_at", "—"),
            "desktop_count":   str(len(desktops)),
            "desktop_names":   " ✦ ".join(desktops.values()) if desktops else "—",
            "collection_count": str(len(data.get("collections", [])))
        }
        for key, val in mapping.items():
            label = self.meta_labels.get(key)
            if label:
                label.config(text=val, foreground="#000")

    def _restore_workspace(self):
        selected = self.restore_dropdown.get()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a workspace to restore")
            return
        restore_apps = self.restore_apps.get()
        restore_schema = self.restore_schema.get()
        # Restore wiring — to be implemented when Workspace orchestration is built
        print(f"[DEBUG] Restoring '{selected}' → Apps: {restore_apps}, Schema: {restore_schema}")

    def _refresh_workspace_list(self):
        files = sorted(self.workspace_dir.glob("*.json"))
        names = [f.stem for f in files]
        self.restore_dropdown["values"] = names
        self.name_combo["values"] = names