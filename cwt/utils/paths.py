# utils/paths.py

"""
Canonical path resolver for CWT.
All storage paths are anchored to the package root (cwt/) so they resolve
correctly regardless of the working directory the app is launched from.
"""

import os
from pathlib import Path

# Anchor: cwt/ package root — one level up from this file (cwt/utils/)
CWT_ROOT = Path(__file__).resolve().parent.parent

SNAPSHOTS_DIR  = CWT_ROOT / "snapshots"
WORKSPACES_DIR = CWT_ROOT / "storage" / "workspaces"
STORAGE_DIR    = CWT_ROOT / "storage"

def get_snapshots_dir() -> Path:
    """Returns the canonical snapshots directory, creating it if needed."""
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    return SNAPSHOTS_DIR

def get_workspaces_dir() -> Path:
    """Returns the canonical workspaces directory, creating it if needed."""
    WORKSPACES_DIR.mkdir(parents=True, exist_ok=True)
    return WORKSPACES_DIR

def get_desktop_path() -> Path:
    """Returns the true local Desktop path, ignoring OneDrive redirection."""
    return Path(os.environ["USERPROFILE"]) / "Desktop"