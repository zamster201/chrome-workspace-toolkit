import tkinter as tk
import gc

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.advanced_mode = tk.BooleanVar(master=self.root, value=False)
        self.root.title("Chrome Workspace Toolkit")
        self.root.geometry("680x620")
        print("✅ MainWindow initialized")

def scan_roots():
    print("🔍 SCANNING FOR tk.Tk() INSTANCES...")
    for obj in gc.get_objects():
        try:
            if isinstance(obj, tk.Tk):
                print("   →", obj, "Title:", obj.title())
        except Exception:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.after(1500, scan_roots)
    root.mainloop()