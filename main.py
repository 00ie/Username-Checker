import os
import sys
import ctypes
from gui.main_window import MainWindow

def configure_environment():
    if sys.platform.startswith('win'):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
            
    required_dirs = ['logs', 'exports', 'config']
    for directory in required_dirs:
        os.makedirs(directory, exist_ok=True)

if __name__ == "__main__":
    configure_environment()
    app = MainWindow()
    app.run()
