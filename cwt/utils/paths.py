# utils/paths.py

"""
Path utilities for CWT – resolves known folders like Desktop.
"""

import os

def get_desktop_path():
    """Returns the true local Desktop path, ignoring OneDrive redirection."""
    return os.path.join(os.environ["USERPROFILE"], "Desktop")

def get_snapshots_path():
    """Returns path to snapshots folder under toolkit root."""
    base = os.path.dirname(os.path.abspath(__file__))  # /utils
    return os.path.join(base, "..", "snapshots")
