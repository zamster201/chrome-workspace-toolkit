# Context Workspace Toolkit (CWT)

**CWT** is a GUI-based utility for capturing, restoring, and managing multi-desktop windows workspaces — designed for power users, researchers, and creators juggling multiple applications, profiles, and windows.

## 🧩 Features

- 🧠 Capture full workspace snapshots (apps + window positions)
- 🔁 Restore windows to original desktops and coordinates
- 📂 Organize by workspace + snapshot name
- 🧰 Auto-create shortcuts for Chrome profiles
- 🧼 Audit & repair default Windows folder mappings
- 🎛️ Fully scriptable and version-controlled

## 🚀 Getting Started

1. Clone the repo:

   git clone https://github.com/zamster201/context-workspace-toolkit.git
   
   
Install dependencies:

pip install -r requirements.txt

Run the app:

python main.py

NOTE: CWT requires pyvda and VirtualDesktopAccessor (included) for Windows virtual desktop(s) management (No additional setup is required)

📁 Folder Structure

CWT/
├── core/               # Snapshot and restore logic
├── gui/                # All Tkinter GUI tabs
├── snapshots/          # Saved workspace configurations
├── utils/              # Low-level helpers (logging, desktop, path audit)
├── scripts/            # Optional CLI or test scripts
└── main.py             # App entry point

💡 Why CWT?
Modern workflows are multi-window, multi-profile, and multi-context. CWT captures your entire working environment — so you can reset, restore, or rapidly pivot across tasks without wasting time.

⚙️ System Requirements
Windows 10/11

Python 3.10+

Admin rights (for full restore support)

🛠️ Roadmap 

 - Multi-browser support (Brave, Edge, Firefox)

 - Profile template generator

 - Workspace autosave & versioning

 - PowerShell automation layer## Virtual Desktop Integration

This toolkit relies on [VirtualDesktopAccessor](https://github.com/Ciantic/VirtualDesktopAccessor) via the `pyvda` Python wrapper. A preconfigured copy is included directly in this repo to ensure reliable cross-desktop functionality out of the box.

No manual installation or compilation is needed.
