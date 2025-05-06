import tkinter as tk
from tkinter import ttk
from tooltip import ToolTip  # your actual tooltip.py

root = tk.Tk()
root.geometry("400x200")

btn = ttk.Button(root, text="Hover me")
btn.pack(pady=50)
ToolTip(btn, "This is a tooltip!")

root.mainloop()
