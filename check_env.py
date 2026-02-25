# check_env.py — run this from C:\CTS\CWT with whichever python launches CWT
# python check_env.py

import sys
import os

print("=== Python Executable ===")
print(sys.executable)

print("\n=== Active venv ===")
print(os.environ.get("VIRTUAL_ENV", "NOT IN A VENV"))

print("\n=== sys.path (where imports resolve from) ===")
for p in sys.path:
    print(f"  {p}")

print("\n=== Key package locations ===")
for pkg in ["pyvda", "fuzzywuzzy", "win32gui", "win32con"]:
    try:
        mod = __import__(pkg)
        print(f"  {pkg}: {getattr(mod, '__file__', 'built-in/no file')}")
    except ImportError:
        print(f"  {pkg}: NOT FOUND")