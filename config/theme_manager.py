import sys
import os
import tkinter as tk
from tkinter import ttk

THEMES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'themes python')
SV_THEME_DIR = os.path.join(THEMES_DIR, 'Sun-Valley-ttk-theme-main')
sys.path.insert(0, SV_THEME_DIR)

try:
    import sv_ttk
    SV_TTK_AVAILABLE = True
    
except ImportError as e:
    SV_TTK_AVAILABLE = False
    


class ThemeManager:
    
    THEMES = {
        'sun-valley-dark': {
            'name': 'Sun Valley Dark',
            'type': 'sv_ttk',
            'mode': 'dark'
        },
        'sun-valley-light': {
            'name': 'Sun Valley Light',
            'type': 'sv_ttk',
            'mode': 'light'
        }
    }
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.current_theme = None
        self._loaded_tcl_themes = set()
        
    
    def apply_theme(self, theme_key: str) -> bool:
        if theme_key not in self.THEMES:
            
            return False
        
        if theme_key == self.current_theme:
            
            return True
        
        
        
        theme_config = self.THEMES[theme_key]
        
        try:
            if SV_TTK_AVAILABLE:
                mode = theme_config['mode']
                
                
                try:
                    current = ttk.Style().theme_use()
                        
                except:
                    pass
                
                sv_ttk.set_theme(mode)
                
                try:
                    current = ttk.Style().theme_use()
                    
                except:
                    pass
            else:
                self._load_sv_manual(theme_config['mode'])
            
            self.current_theme = theme_key
            
            return True
            
        except Exception:
            return False
    
    def _load_sv_manual(self, mode: str):
        sv_tcl = os.path.join(SV_THEME_DIR, 'sv_ttk', 'sv.tcl')
        if os.path.exists(sv_tcl):
            self.root.tk.call('source', sv_tcl)
            ttk.Style().theme_use(f'sun-valley-{mode}')
    
    def toggle_mode(self):
        if 'dark' in self.current_theme:
            new_theme = self.current_theme.replace('dark', 'light')
        else:
            new_theme = self.current_theme.replace('light', 'dark')
        
        self.apply_theme(new_theme)
    
    def get_available_themes(self) -> list:
        return [(key, config['name']) for key, config in self.THEMES.items()]
    
    def get_current_theme(self) -> str:
        return self.current_theme
    
    def is_dark_mode(self) -> bool:
        return 'dark' in self.current_theme


_theme_manager = None

def get_theme_manager(root: tk.Tk = None) -> ThemeManager:
    global _theme_manager
    if _theme_manager is None and root is not None:
        _theme_manager = ThemeManager(root)
    return _theme_manager
