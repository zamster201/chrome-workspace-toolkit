"""
Module: main.py
Part of: Chrome Workspace Toolkit (CWT)

Description:
    Entry point for the CWT application. Initializes the main window and GUI tabs.

Author: Tom
Last Updated: 2025-03-31
"""

import tkinter as tk
from gui.main_window import MainWindow

def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == '__main__':
    main()
