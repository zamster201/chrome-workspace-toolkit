import tkinter as tk
print("Before root:", tk._default_root)

root = tk.Tk()
root.geometry("300x150")
tk.Label(root, text="Clean test").pack()

def check_extra():
    print("Root after:", tk._default_root)
    for w in root.winfo_children():
        print("  ↪", w)

import gc
for obj in gc.get_objects():
    if isinstance(obj, tk.Tk):
        print("ROOT FOUND:", obj)

root.after(1000, check_extra)
root.mainloop()