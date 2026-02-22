import os
import json
import sys  # <- make sure this is here if you're using sys.path.append
import pathlib
import importlib.util

# Construct path to patch_preferences.py
script_path = pathlib.Path(__file__).parent / "patch_preferences.py"

# Load it as a module
spec = importlib.util.spec_from_file_location("patch_preferences", script_path)
patch_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch_mod)

# Use the function
patch_mod.patch_restore_on_startup("Boomers")