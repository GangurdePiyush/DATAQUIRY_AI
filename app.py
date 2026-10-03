"""
app.py
------
Main application launcher for the Simple Dataset Upload & Query System.

Running this script launches the Tkinter Desktop GUI:
    python app.py
"""

import sys
import os

# Ensure project root is in Python module search path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ui.main_window import MainWindow


def main():
    """Initializes and runs the desktop application."""
    print("Launching Simple Dataset Upload & Query System (Part 1)...")
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
