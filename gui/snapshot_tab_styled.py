
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import json
from utils.tooltip import ToolTip
from core.snapshot_capture import capture_snapshot
from core.restore import restore_windows


class SnapshotTab(ttk.Frame):
    def __init__(self, master, advanced_mode):
        super().__init__(master)
        self.advanced_mode = advanced_mode
        self.snapshot_dir = Path("storage/snapshots")
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.meta_labels = {}
        self.snapshot_var = tk.StringVar()
        self.restore_var = tk.StringVar()
        self._build_ui()

    def _build_ui(self):
        header = ttk.Label(self, text="Snapshot Collection Management", style="Header.TLabel")
        header.pack(pady=(8, 0))

        self.adv_check = ttk.Checkbutton(self, text="Advanced Mode", variable=self.advanced_mode)
        self.adv_check.pack(anchor="ne", padx=20, pady=(5, 0))
        ToolTip(self.adv_check, "Show debug output and snapshot metadata.")

        save_frame = ttk.LabelFrame(self, text="Save Snapshot Collection", style="Bold.TLabelframe")
        save_frame.pack(fill="x", padx=20, pady=(10, 5))

        ttk.Label(save_frame, text="Collection Name:").pack(anchor="w", padx=10, pady=(5, 0))
        self.snapshot_entry = ttk.Entry(save_frame, textvariable=self.snapshot_var, width=40)
        self.snapshot_entry.pack(padx=10, pady=5)

        save_btn = ttk.Button(save_frame, text="📸 Create Collection", command=self._handle_capture)
        save_btn.pack(pady=(0, 10))
        ToolTip(save_btn, "Save a snapshot of all current Chrome windows.")

        restore_frame = ttk.LabelFrame(self, text="Restore Snapshot Collection", style="Bold.TLabelframe")
        restore_frame.pack(fill="x", padx=20, pady=(5, 10))

        ttk.Label(restore_frame, text="Collection Name:").pack(anchor="w", padx=10, pady=(5, 0))
        self.restore_dropdown = ttk.Combobox(restore_frame, textvariable=self.restore_var, values=self._get_collections(), width=38)
        self.restore_dropdown.pack(padx=10, pady=5)

        restore_btn = ttk.Button(restore_frame, text="🧩 Restore Collection", command=self._handle_restore)
        restore_btn.pack(pady=(0, 10))
        ToolTip(restore_btn, "Restore windows from the selected snapshot collection.")

        self.meta_frame = ttk.LabelFrame(self, text="Snapshot Metadata", style="Bold.TLabelframe")
        self.meta_frame.pack(fill="x", padx=20, pady=(0, 10))
        for key in ["workspace", "collection_id", "captured_at", "desktop_count", "desktop_names", "snapshot_file"]:
            row = ttk.Frame(self.meta_frame)
            row.pack(fill="x", padx=5, pady=1)
            label = ttk.Label(row, text=f"{key.replace('_', ' ').title()}:", width=16, anchor="w")
            label.pack(side="left")
            value = ttk.Label(row, text="", anchor="w")
            value.pack(side="left", fill="x", expand=True)
            self.meta_labels[key] = value

        self.debug_output = tk.Text(self, height=6, state="disabled", background="#1e1e1e", foreground="#dcdcdc")
        self.debug_output.pack(fill="x", padx=20, pady=(0, 10))

    def _get_collections(self):
        return sorted([f.name for f in self.snapshot_dir.iterdir() if f.is_dir()])

    def _handle_capture(self):
        name = self.snapshot_var.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Please enter a name for the snapshot collection.")
            return

        existing = self._get_collections()
        if name in existing:
            confirm = messagebox.askyesno("Overwrite?", f"Collection '{name}' already exists. Overwrite?")
            if not confirm:
                return

        snapshot_path = capture_snapshot(
            workspace_name=name,
            logger=self._log,
            gui_callback=lambda meta: self._show_metadata({**meta, "snapshot_file": Path(snapshot_path).name})
        )
        self._log(f"[✓] Snapshot saved to: {snapshot_path}")
        self.restore_dropdown["values"] = self._get_collections()

    def _handle_restore(self):
        name = self.restore_var.get().strip()
        if not name:
            messagebox.showwarning("No Selection", "Please select a collection to restore.")
            return

        snap_dir = self.snapshot_dir / name
        if not snap_dir.exists():
            messagebox.showerror("Not Found", f"Snapshot folder '{name}' not found.")
            return

        snapshots = sorted(snap_dir.glob("snapshot_*.json"), reverse=True)
        if not snapshots:
            messagebox.showwarning("No Snapshots", f"No snapshots found in '{name}'.")
            return

        snapshot_path = snapshots[0]
        restore_windows(str(snapshot_path), logger=self._log)
        with open(snapshot_path, "r", encoding="utf-8") as f:
            snapshot = json.load(f)
        self._show_metadata({
            "workspace": snapshot.get("workspace"),
            "collection_id": snapshot.get("collection_id"),
            "captured_at": snapshot.get("captured_at"),
            "desktop_count": len(snapshot.get("desktops", {})),
            "desktop_names": list(snapshot.get("desktops", {}).values()),
            "snapshot_file": snapshot_path.name
        })

    def _log(self, msg):
        if not self.advanced_mode.get():
            return
        self.debug_output.configure(state="normal")
        self.debug_output.insert(tk.END, msg + "\n")
        self.debug_output.see(tk.END)
        self.debug_output.configure(state="disabled")

    def _show_metadata(self, data):
        if not self.advanced_mode.get():
            return
        for k, v in data.items():
            label = self.meta_labels.get(k)
            if label:
                label.config(text=", ".join(v) if isinstance(v, list) else str(v))
