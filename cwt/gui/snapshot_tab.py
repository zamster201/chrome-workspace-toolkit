#gui/snapshot_tab.py

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime
import json
from cwt.utils.tooltip import ToolTip
from cwt.utils.paths import get_snapshots_dir
from cwt.core.snapshot_capture import capture_snapshot
from cwt.core.restore import restore_windows


class SnapshotTab(ttk.Frame):
    def __init__(self, master, advanced_mode):
        super().__init__(master)
        self.advanced_mode = advanced_mode
        self.snapshot_dir = get_snapshots_dir()
        self.meta_labels = {}
        self.snapshot_var = tk.StringVar(master=self)
        self.restore_var = tk.StringVar(master=self)
        self._build_ui()

    def _build_ui(self):
        header = ttk.Label(self, text="Snapshot Collection Management", font=("Segoe UI", 12, "bold"))
        header.pack(pady=(10, 0))

        self.adv_check = ttk.Checkbutton(self, text="Advanced Mode", variable=self.advanced_mode)
        self.adv_check.pack(anchor="ne", padx=20, pady=(5, 0))
        ToolTip(self.adv_check, "Show debug output and snapshot metadata.")

        # --- Create Collection Section ---
        save_frame = ttk.LabelFrame(self, text="  Create Snapshot Collection  ", style="Bold.TLabelframe")
        save_frame.pack(fill="x", padx=20, pady=(10, 7))

        save_row = ttk.Frame(save_frame)
        save_row.pack(fill="x", padx=(10, 10), pady=(5, 5))

        ttk.Label(save_row, text="Collection Name:", style="Header.TLabel").pack(side="left", padx=(12, 14))
        self.snapshot_entry = ttk.Combobox(save_row, textvariable=self.snapshot_var, width=30)
        self.snapshot_entry.pack(side="left", padx=(0, 12))
        ToolTip(self.snapshot_entry, "Enter a name to identify this snapshot collection.")

        self.save_btn = ttk.Button(save_row, text="📸 Create Collection ", command=self._handle_capture)
        self.save_btn.pack(side="left", padx=(0, 5))
        ToolTip(self.save_btn, "Save a snapshot of all current windows")

        ttk.Label(save_frame, text="[ Default Name : SS.DD-MMM-YY_HHMM ]", font=("Segoe UI", 8)).pack(
            anchor="w", padx=(125, 10), pady=(2, 10))

        # Filter checkboxes — single row, properly wired
        check_row = ttk.Frame(save_frame)
        check_row.pack(fill="x", padx=(24, 5), pady=(0, 10))

        self.chrome_only = tk.BooleanVar(master=self)
        self.app_only = tk.BooleanVar(master=self)

        chrome_check = ttk.Checkbutton(check_row, text="Capture Chrome Windows ONLY", variable=self.chrome_only)
        chrome_check.pack(side="left", padx=(0, 10))
        ToolTip(chrome_check, "Only include Chrome windows in the snapshot")

        app_check = ttk.Checkbutton(check_row, text="Capture Apps ONLY", variable=self.app_only)
        app_check.pack(side="left")
        ToolTip(app_check, "Only include non-Chrome application windows in the snapshot")

        # --- Divider ---
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=20, pady=10)

        # --- Restore Collection Section ---
        restore_frame = ttk.LabelFrame(self, text="  Restore Snapshot Collection", style="Bold.TLabelframe")
        restore_frame.pack(fill="x", padx=20, pady=(0, 10))

        restore_row = ttk.Frame(restore_frame)
        restore_row.pack(fill="x", padx=10, pady=(5, 7))

        ttk.Label(restore_row, text="Collection Name:", style="Header.TLabel").pack(side="left", padx=(12, 15))

        self.restore_dropdown = ttk.Combobox(
            restore_row,
            textvariable=self.restore_var,
            values=self._get_collections(),
            state="readonly",
            width=30
        )
        self.restore_dropdown.pack(side="left", padx=(0, 10))

        restore_btn = ttk.Button(restore_row, text="🧩 Restore Collection ", command=self._handle_restore)
        restore_btn.pack(side="left")
        ToolTip(restore_btn, "Restore windows from the selected snapshot collection")

        ttk.Label(restore_frame, text="[ Select a Snapshot Collection ]", font=("Segoe UI", 8)).pack(
            anchor="w", padx=(153, 5), pady=(0, 10))

        # --- Metadata Section (always visible) ---
        self.meta_frame = ttk.LabelFrame(self, text="Snapshot Metadata", style="Bold.TLabelframe")
        self.meta_frame.pack(fill="x", padx=20, pady=(0, 5))

        for key in ["collection_name", "collection_id", "captured_at", "desktop_count", "desktop_names", "snapshot_file"]:
            row = ttk.Frame(self.meta_frame)
            row.pack(fill="x", padx=5, pady=1)
            ttk.Label(row, text=f"{key.replace('_', ' ').title()}:", width=16, anchor="w").pack(side="left")
            value = ttk.Label(row, text="—", anchor="w", foreground="#555")
            value.pack(side="left", fill="x", expand=True)
            self.meta_labels[key] = value

        # --- Debug Output (Advanced Mode only) ---
        self.debug_output = tk.Text(self, height=6, state="disabled", background="#1e1e1e", foreground="#dcdcdc")
        self.debug_output.pack(fill="x", padx=20, pady=(0, 10))

    def _get_collections(self):
        return sorted([f.name for f in self.snapshot_dir.iterdir() if f.is_dir()])

    def _refresh_dropdowns(self):
        collections = self._get_collections()
        self.restore_dropdown["values"] = collections
        self.snapshot_entry["values"] = collections

    def _handle_capture(self):
        name = self.snapshot_var.get().strip()
        if not name:
            name = "SS." + datetime.now().strftime("%d-%b-%Y_%H%M")
            self.snapshot_var.set(name)

        existing = self._get_collections()
        if name in existing:
            if not messagebox.askyesno("Add Snapshot?", f"Collection '{name}' already exists.\nAdd another snapshot to it?"):
                return

        snapshot_path = capture_snapshot(
            collection_name=name,
            logger=self._log,
            gui_callback=self._show_metadata,
            chrome_only=self.chrome_only.get(),
            app_only=self.app_only.get()
        )
        self._show_metadata({"snapshot_file": Path(snapshot_path).name})
        self._log(f"[✓] Snapshot saved to: {snapshot_path}")
        self._refresh_dropdowns()

    def _handle_restore(self):
        name = self.restore_var.get().strip()
        if not name:
            messagebox.showwarning("No Selection", "Please select a collection to restore")
            return

        snap_dir = self.snapshot_dir / name
        if not snap_dir.exists():
            messagebox.showerror("Not Found", f"Snapshot folder '{name}' not found")
            return

        snapshots = sorted(snap_dir.glob("snapshot_*.json"), reverse=True)
        if not snapshots:
            messagebox.showwarning("No Snapshots", f"No snapshots found in '{name}'")
            return

        snapshot_path = snapshots[0]
        restore_windows(str(snapshot_path), logger=self._log)

        with open(snapshot_path, "r", encoding="utf-8") as f:
            snapshot = json.load(f)

        self._show_metadata({
            "collection_name": snapshot.get("collection_name") or snapshot.get("workspace", name),
            "collection_id":   snapshot.get("collection_id"),
            "captured_at":     snapshot.get("captured_at"),
            "desktop_count":   len(snapshot.get("desktops", {})),
            "desktop_names":   list(snapshot.get("desktops", {}).values()),
            "snapshot_file":   snapshot_path.name
        })

    def _log(self, msg):
        if not self.advanced_mode.get():
            return
        self.debug_output.configure(state="normal")
        self.debug_output.insert(tk.END, msg + "\n")
        self.debug_output.see(tk.END)
        self.debug_output.configure(state="disabled")

    def _show_metadata(self, data: dict):
        """Populate metadata panel — always visible, no Advanced Mode gate."""
        for k, v in data.items():
            label = self.meta_labels.get(k)
            if label:
                label.config(
                    text=" ✦ ".join(str(i) for i in v) if isinstance(v, list) else str(v),
                    foreground="#000"
                )