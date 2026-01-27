import os
import sys
import ctypes
import threading
from gui.app_window import AppWindow

def _validate_startup_proxies():
    try:
        from core.proxy_checker import load_proxies, check_proxies
        proxies = load_proxies("proxies.txt")
        if proxies:
            def _worker():
                try:
                    check_proxies(proxies, workers=min(50, max(5, len(proxies))))
                except Exception as e:
                    pass

            t = threading.Thread(target=_worker, daemon=True)
            t.start()
    except Exception:
        pass

def configure_environment():
    if sys.platform.startswith('win'):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
            
    required_dirs = ['logs', 'exports', 'config', 'data']
    for directory in required_dirs:
        os.makedirs(directory, exist_ok=True)

if __name__ == "__main__":
    configure_environment()
    _validate_startup_proxies()
    app = AppWindow()
    app.run()
