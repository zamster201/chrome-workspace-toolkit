import os
import json
from pathlib import Path

def patch_restore_on_startup(profile_name):
    user_data = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
    prefs_path = Path(user_data) / profile_name / "Preferences"

    if not prefs_path.exists():
        print(f"[!] Preferences not found for profile: {profile_name}")
        return

    # Backup before modifying
    backup_path = prefs_path.with_suffix(".bak")
    prefs_path.replace(backup_path)
    print(f"[+] Backup created: {backup_path}")

    # Read original (ugly, one-liner JSON)
    try:
        with backup_path.open("r", encoding="utf-8") as f:
            prefs = json.load(f)
    except Exception as e:
        print(f"[!] Failed to parse JSON: {e}")
        return

    # Inject or update the setting
    prefs.setdefault("session", {})
    prefs["session"]["restore_on_startup"] = 1

    # Write back with pretty formatting
    print(f"[DEBUG] Patching: {prefs_path}")
    print(f"[DEBUG] Current session settings: {prefs.get('session', {})}")

    try:
        with prefs_path.open("w", encoding="utf-8") as f:
            json.dump(prefs, f, indent=2)

        print(f"[DEBUG] New session settings: {prefs['session']}")
        print("[DEBUG] Write complete.")
        print(f"[✓] Patched profile '{profile_name}' to restore tabs on startup.")

    except Exception as e:
        print(f"[!] Failed to write modified prefs: {e}")
