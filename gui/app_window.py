import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import random
import string
import os
import csv
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from gui.ui_components import ModernUI
from gui.widgets import Toast
from utils.notifications import notification_manager
from utils.animations import AnimationEngine
from utils.validators import InputValidator
from utils.database import db
from core.engine import AuditEngine
from config.settings import settings
from config.theme_manager import get_theme_manager
from core.platforms import ProxyManager
from core.proxy_checker import check_proxies


class AppWindow:
    
    def __init__(self):
        
        
        self.root = tk.Tk()
        self.root.title("Username Checker")
        self.root.geometry("1000x700")
        self.root.minsize(950, 650)
        
        try:
            self.root.tk.call('tk', 'useinputmethods', '-displayof', self.root, False)
        except:
            pass
        
        
        self.root.withdraw()
        self.root.resizable(True, True)
        
        try:
            import ctypes
            from ctypes import wintypes
            self.root.update_idletasks()
            hwnd = self.root.winfo_id()
            hwnd = ctypes.c_void_p(hwnd)
            DWM_BLURBEHIND = ctypes.c_int
            DWMWA_NCRENDERING_POLICY = 2
            DWMNCRP_DISABLED = 1
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_NCRENDERING_POLICY,
                ctypes.byref(ctypes.c_int(DWMNCRP_DISABLED)),
                ctypes.sizeof(ctypes.c_int)
            )
            
            DWMWA_TRANSITIONS_FORCEDISABLED = 3
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_TRANSITIONS_FORCEDISABLED,
                ctypes.byref(ctypes.c_int(1)),
                ctypes.sizeof(ctypes.c_int)
            )
            DWMWA_DISALLOW_PEEK = 12
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_DISALLOW_PEEK,
                ctypes.byref(ctypes.c_int(1)),
                ctypes.sizeof(ctypes.c_int)
            )
            
            GWL_EXSTYLE = -20
            WS_EX_COMPOSITED = 0x02000000
            WS_EX_LAYERED = 0x00080000
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            new_style = style & ~(WS_EX_COMPOSITED | WS_EX_LAYERED)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
            
            
        except Exception:
            pass
        
        self.root.configure(bg='#1c1c1c')
        
        
        self.theme_manager = get_theme_manager(self.root)
        
        self.theme_manager.current_theme = None
        
        success = self.theme_manager.apply_theme('sun-valley-dark')
        
        if self.theme_manager.current_theme != 'sun-valley-dark':
            
            self.theme_manager.current_theme = None
            self.theme_manager.apply_theme('sun-valley-dark')
        
        style = ttk.Style()
        style.configure('Card.TFrame', relief='flat', borderwidth=0)
        style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'))
        
        style.layout('TButton', [
            ('Button.border', {'sticky': 'nswe', 'border': '1', 'children': [
                ('Button.padding', {'sticky': 'nswe', 'children': [
                    ('Button.label', {'sticky': 'nswe'})
                ]})
            ]})
        ])
        style.layout('TCheckbutton', [
            ('Checkbutton.padding', {'sticky': 'nswe', 'children': [
                ('Checkbutton.indicator', {'side': 'left', 'sticky': ''}),
                ('Checkbutton.label', {'sticky': 'nswe'})
            ]})
        ])
        
        style.map('TButton', 
                  focuscolor=[],
                  foreground=[],
                  background=[])
        style.map('TCheckbutton',
                  focuscolor=[],
                  foreground=[],
                  background=[])
        style.map('TEntry',
                  focuscolor=[],
                  fieldbackground=[])
        style.configure('TNotebook', borderwidth=0)
        style.configure('TNotebook.Tab', focuscolor='', highlightthickness=0, padding=[10, 4])
        style.map('TNotebook.Tab',
              focuscolor=[('focus', '#2a2a2a'), ('selected', '#2a2a2a')],
              bordercolor=[('focus', '#2a2a2a'), ('selected', '#2a2a2a')],
              lightcolor=[('focus', '#2a2a2a'), ('selected', '#2a2a2a')],
              darkcolor=[('focus', '#2a2a2a'), ('selected', '#2a2a2a')])
        
        self.root.option_add('*highlightThickness', 0)
        
        
        try:
            import pywinstyles
            import sys
            version = sys.getwindowsversion()
            
            if version.major == 10 and version.build >= 22000:
                
                pywinstyles.change_header_color(self.root, "#1c1c1c")
                pywinstyles.apply_style(self.root, "optimised")
                
            elif version.major == 10:
                
                pywinstyles.apply_style(self.root, "optimised")
                
        except ImportError:
            pass
        except Exception:
            pass
        
        self.engine = AuditEngine()
        self.targets: List[str] = []
        self.results_cache: List[Dict[str, Any]] = []
        self.session_id = str(uuid.uuid4())
        self.stat_total = tk.IntVar(value=0)
        self.stat_avail = tk.IntVar(value=0)
        self.stat_rate = tk.StringVar(value="0%")
        self.stat_speed = tk.StringVar(value="0/s")
        self.hide_taken = tk.BooleanVar(value=False)
        self.auto_export = tk.BooleanVar(value=False)
        self.use_proxies = tk.BooleanVar(value=settings.get("use_proxies", False))
        self.desktop_notifications = tk.BooleanVar(value=True)
        self.current_theme = tk.StringVar(value="dark")
        self.start_time: Optional[float] = None
        self.last_check_time: Optional[float] = None
        self.load_icon()
        
        self.setup_shortcuts()
        
        self.build_ui()
        
        self._disable_focus_globally(self.root)
        
        db.create_session(self.session_id, {
            'platforms': self.get_enabled_platforms(),
            'use_proxies': self.use_proxies.get()
        })
        try:
            self._log_to_console("Username Checker initialized!", "success")
            self._log_to_console(f"Session ID: {self.session_id[:8]}...", "info")
        except Exception as e:
            pass
        self.root.after(60000, self.auto_save)
    
    def _disable_focus_globally(self, widget):
        try:
            widget_class = widget.winfo_class()
            allow_focus = widget_class in {"TEntry", "Entry", "Text", "TCombobox"}
            if hasattr(widget, 'configure') and not allow_focus:
                try:
                    widget.configure(takefocus=0)
                except:
                    pass
            if hasattr(widget, 'configure'):
                try:
                    widget.configure(highlightthickness=0)
                except:
                    pass
            for child in widget.winfo_children():
                self._disable_focus_globally(child)
        except:
            pass
    
    def load_icon(self):
        ico_path = os.path.join("assets", "icon.ico")
        if os.path.exists(ico_path):
            try:
                self.root.iconbitmap(ico_path)
                return
            except:
                pass
        paths = ["icon.jpg", "assets/icon.jpg", "image.jpg", "icon.png", "assets/icon.png"]
        for path in paths:
            if os.path.exists(path):
                try:
                    self.root.iconphoto(False, tk.PhotoImage(file=path))
                    break
                except:
                    pass
    
    def setup_shortcuts(self):
        self.root.bind_all('<Control-s>', lambda e: self.export_results())
        self.root.bind_all('<Control-g>', lambda e: self.generate_usernames())
        self.root.bind_all('<Control-r>', lambda e: self.start_bulk())
        self.root.bind_all('<Control-Shift-R>', lambda e: self.stop_audit())
        self.root.bind_all('<Control-q>', lambda e: self.on_closing())
        self.root.bind_all('<F5>', lambda e: self.refresh_ui())
        self.root.bind_all('<Control-1>', lambda e: self.tab_control.select(0))
        self.root.bind_all('<Control-2>', lambda e: self.tab_control.select(1))
        self.root.bind_all('<Control-3>', lambda e: self.tab_control.select(2))
        self.root.bind_all('<Control-4>', lambda e: self.tab_control.select(3))
        self.root.bind_all('<Control-5>', lambda e: self.tab_control.select(4))
        self.root.bind_all('<Control-6>', lambda e: self.tab_control.select(5))
        self.root.bind_all('<Control-Key-1>', lambda e: self.tab_control.select(0))
        self.root.bind_all('<Control-Key-2>', lambda e: self.tab_control.select(1))
        self.root.bind_all('<Control-Key-3>', lambda e: self.tab_control.select(2))
        self.root.bind_all('<Control-Key-4>', lambda e: self.tab_control.select(3))
        self.root.bind_all('<Control-Key-5>', lambda e: self.tab_control.select(4))
        self.root.bind_all('<Control-Key-6>', lambda e: self.tab_control.select(5))
        self.root.bind_all('<Control-KP_1>', lambda e: self.tab_control.select(0))
        self.root.bind_all('<Control-KP_2>', lambda e: self.tab_control.select(1))
        self.root.bind_all('<Control-KP_3>', lambda e: self.tab_control.select(2))
        self.root.bind_all('<Control-KP_4>', lambda e: self.tab_control.select(3))
        self.root.bind_all('<Control-KP_5>', lambda e: self.tab_control.select(4))
        self.root.bind_all('<Control-KP_6>', lambda e: self.tab_control.select(5))
        
        self._is_moving = False
        self._suspend_rendering = False
        self._last_minimize_time = 0
        self._last_restore_time = 0
        self.root.bind('<ButtonPress-1>', self._on_drag_start)
        self.root.bind('<ButtonRelease-1>', self._on_drag_end)
        self.root.bind('<B1-Motion>', self._on_dragging)
        self.root.bind('<Unmap>', self._on_minimize)
        self.root.bind('<Map>', self._on_restore)
    
    def _on_drag_start(self, event):
        if event.y < 40:
            self._is_moving = True
            self._suspend_rendering = True
    
    def _on_dragging(self, event):
        if self._is_moving:
            return "break"
    
    def _on_drag_end(self, event):
        if self._is_moving:
            self._is_moving = False
            self._suspend_rendering = False
            
            self.root.after(50, lambda: self.root.update_idletasks())
    
    def _on_minimize(self, event):
        import time
        now = time.time()
        if now - self._last_minimize_time < 0.1:
            return
        self._last_minimize_time = now
        
        if not self._suspend_rendering:
            self._suspend_rendering = True
            
    
    def _on_restore(self, event):
        import time
        now = time.time()
        if now - self._last_restore_time < 0.1:
            return
        self._last_restore_time = now
        
        if self._suspend_rendering:
            self._suspend_rendering = False
            
            self.root.update_idletasks()
    
    def build_ui(self):
        self.create_header()
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))
        self.create_tabs(main_container)
        self.create_footer()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_header(self):
        header = ttk.Frame(self.root, style='Card.TFrame')
        header.pack(fill=tk.X, padx=10, pady=(10, 5))
        header_content = ttk.Frame(header, padding=8)
        header_content.pack(fill=tk.X)
        left_frame = ttk.Frame(header_content)
        left_frame.pack(side=tk.LEFT)
        title_frame = ttk.Frame(left_frame)
        title_frame.pack(anchor='w')
        
        ttk.Label(
            title_frame,
            text="USERNAME CHECKER",
            font=('Segoe UI', 14, 'bold')
        ).pack(side=tk.LEFT)
        
        ttk.Label(
            left_frame,
            text="Find available usernames across multiple platforms",
            font=('Segoe UI', 8)
        ).pack(anchor='w', pady=(2, 0))
        
        stats_container = ttk.Frame(header_content)
        stats_container.pack(side=tk.RIGHT, padx=10)
        checked_frame = ttk.Frame(stats_container, style='Card.TFrame', padding=8)
        checked_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(
            checked_frame,
            text="CHECKED",
            font=('Segoe UI', 7)
        ).pack()
        
        ttk.Label(
            checked_frame,
            textvariable=self.stat_total,
            font=('Segoe UI', 12, 'bold')
        ).pack()
        
        avail_frame = ttk.Frame(stats_container, style='Card.TFrame', padding=8)
        avail_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(
            avail_frame,
            text="AVAILABLE",
            font=('Segoe UI', 7)
        ).pack()
        
        ttk.Label(
            avail_frame,
            textvariable=self.stat_avail,
            font=('Segoe UI', 12, 'bold')
        ).pack()
        
        rate_frame = ttk.Frame(stats_container, style='Card.TFrame', padding=8)
        rate_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(
            rate_frame,
            text="RATE",
            font=('Segoe UI', 7)
        ).pack()
        
        ttk.Label(
            rate_frame,
            textvariable=self.stat_speed,
            font=('Segoe UI', 12, 'bold')
        ).pack()
    
    def create_tabs(self, parent: tk.Widget):
        
        self.tab_control = ttk.Notebook(parent, padding=5, takefocus=False)
        
        self.tab_bulk = ttk.Frame(self.tab_control, takefocus=False)
        self.tab_monitor = ttk.Frame(self.tab_control, takefocus=False)
        self.tab_proxies = ttk.Frame(self.tab_control, takefocus=False)
        self.tab_settings = ttk.Frame(self.tab_control, takefocus=False)
        self.tab_webhook = ttk.Frame(self.tab_control, takefocus=False)
        self.tab_about = ttk.Frame(self.tab_control, takefocus=False)
        
        self.tab_control.add(self.tab_bulk, text='BULK CHECKER')
        self.tab_control.add(self.tab_monitor, text='MONITOR')
        self.tab_control.add(self.tab_proxies, text='PROXIES')
        self.tab_control.add(self.tab_settings, text='SETTINGS')
        self.tab_control.add(self.tab_webhook, text='WEBHOOK')
        self.tab_control.add(self.tab_about, text='ABOUT')
        
        self.tab_control.pack(fill=tk.BOTH, expand=True, pady=20)
        
        self._built_tabs = set()
        
        self.build_bulk_tab()
        self._built_tabs.add("bulk")
        
        self.tab_control.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _on_tab_changed(self, event=None):
        selected = self.tab_control.nametowidget(self.tab_control.select())
        if selected is self.tab_monitor and "monitor" not in self._built_tabs:
            self.build_monitor_tab()
            self._built_tabs.add("monitor")
            return
        if selected is self.tab_proxies and "proxies" not in self._built_tabs:
            self.build_proxies_tab()
            self._built_tabs.add("proxies")
            return
        if selected is self.tab_settings and "settings" not in self._built_tabs:
            self.build_settings_tab()
            self._built_tabs.add("settings")
            return
        if selected is self.tab_webhook and "webhook" not in self._built_tabs:
            self.build_webhook_tab()
            self._built_tabs.add("webhook")
            return
        if selected is self.tab_about and "about" not in self._built_tabs:
            self.build_about_tab()
            self._built_tabs.add("about")
    
    def build_bulk_tab(self):
        container = ttk.Frame(self.tab_bulk)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        sidebar_container = ttk.Frame(container, width=300)
        sidebar_container.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        sidebar_container.pack_propagate(False)
        canvas = tk.Canvas(sidebar_container, bg='#1c1c1c', highlightthickness=0, takefocus=0)
        scrollbar = ttk.Scrollbar(sidebar_container, orient="vertical", command=canvas.yview)
        sidebar = ttk.Frame(canvas)
        
        sidebar.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=sidebar, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        config_frame = ttk.Frame(sidebar, style='Card.TFrame')
        config_frame.pack(fill=tk.X, pady=(0, 5))
        
        config_content = ttk.Frame(config_frame, padding=8)
        config_content.pack(fill=tk.X)
        
        ttk.Label(
            config_content,
            text="CONFIGURATION",
            font=('Segoe UI', 11, 'bold')
        ).pack(anchor='w', pady=(0, 15))
        
        ttk.Label(
            config_content,
            text="Platforms to Check",
            font=('Segoe UI', 9, 'bold')
        ).pack(anchor='w', pady=(0, 10))
        
        self.platform_vars = {
            "pinterest": tk.BooleanVar(value=settings.get("platforms.pinterest", True)),
            "instagram": tk.BooleanVar(value=settings.get("platforms.instagram", True)),
            "github": tk.BooleanVar(value=settings.get("platforms.github", True))
        }
        
        for platform, var in self.platform_vars.items():
            ttk.Checkbutton(
                config_content,
                text=f"{platform.title()}",
                variable=var,
                style='Switch.TCheckbutton'
            ).pack(anchor='w', pady=5, padx=5)
        
        ttk.Separator(config_content, orient='horizontal').pack(fill=tk.X, pady=15)
        
        ttk.Label(
            config_content,
            text="Generation Settings",
            font=('Segoe UI', 9, 'bold')
        ).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(
            config_content,
            text="Username Count"
        ).pack(anchor='w')
        
        self.count_entry = ttk.Entry(config_content, takefocus=False)
        self.count_entry.pack(fill=tk.X, pady=(5, 10))
        self.count_entry.insert(0, "100")
        
        ttk.Label(
            config_content,
            text="Username Length"
        ).pack(anchor='w')
        
        self.length_entry = ttk.Entry(config_content, takefocus=False)
        self.length_entry.pack(fill=tk.X, pady=(5, 10))
        self.length_entry.insert(0, "4")
        
        filters_frame = ttk.Frame(sidebar, style='Card.TFrame')
        filters_frame.pack(fill=tk.X, pady=(0, 5))
        
        filters_content = ttk.Frame(filters_frame, padding=8)
        filters_content.pack(fill=tk.X)
        
        ttk.Label(
            filters_content,
            text="FILTERS",
            font=('Segoe UI', 11, 'bold')
        ).pack(anchor='w', pady=(0, 15))
        
        ttk.Checkbutton(
            filters_content,
            text="Hide Taken Results",
            variable=self.hide_taken,
            style='Switch.TCheckbutton'
        ).pack(anchor='w', pady=5)
        
        ttk.Checkbutton(
            filters_content,
            text="Use Proxies",
            variable=self.use_proxies,
            style='Switch.TCheckbutton'
        ).pack(anchor='w', pady=5)
        
        ttk.Checkbutton(
            filters_content,
            text="Auto-export available",
            variable=self.auto_export,
            style='Switch.TCheckbutton'
        ).pack(anchor='w', pady=5)
        
        actions_frame = ttk.Frame(sidebar)
        actions_frame.pack(fill=tk.X)
        
        ttk.Button(
            actions_frame,
            text="Generate list",
            command=self.generate_usernames
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            actions_frame,
            text="Import file",
            command=self.import_usernames
        ).pack(fill=tk.X, pady=2)
        
        self.bulk_start_btn = ttk.Button(
            actions_frame,
            text="Start checking",
            command=self.start_bulk,
            style='Accent.TButton'
        )
        self.bulk_start_btn.pack(fill=tk.X, pady=2)
        
        ttk.Button(
            actions_frame,
            text="Stop",
            command=self.stop_audit
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            actions_frame,
            text="Export results",
            command=self.export_results
        ).pack(fill=tk.X, pady=2)
        
        main_area = ttk.Frame(container)
        main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        progress_frame = ttk.Frame(main_area)
        progress_frame.pack(fill=tk.X, pady=(0, 5))
        
        progress_info = ttk.Frame(progress_frame)
        progress_info.pack(fill=tk.X, pady=(0, 8))
        
        self.progress_label = ttk.Label(
            progress_info,
            text="Ready to check usernames"
        )
        self.progress_label.pack(side=tk.LEFT)
        
        self.progress_percent = ttk.Label(
            progress_info,
            text="0%",
            font=('Segoe UI', 9, 'bold')
        )
        self.progress_percent.pack(side=tk.RIGHT)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X)
        self.progress_bar['value'] = 0
        
        console_frame = ttk.Frame(main_area, style='Card.TFrame')
        console_frame.pack(fill=tk.BOTH, expand=True)
        
        console_content = ttk.Frame(console_frame, padding=8)
        console_content.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            console_content,
            text="RESULTS LOG",
            font=('Segoe UI', 10, 'bold')
        ).pack(anchor='w', pady=(0, 5))
        
        console_scroll_frame = ttk.Frame(console_content)
        console_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        self.console = tk.Text(
            console_scroll_frame,
            wrap=tk.WORD,
            height=8,
            font=('Consolas', 8),
            bg='#1c1c1c',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            borderwidth=0,
            highlightthickness=0,
            takefocus=0
        )
        scrollbar = ttk.Scrollbar(console_scroll_frame, command=self.console.yview)
        self.console.configure(yscrollcommand=scrollbar.set)
        
        self.console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.console.tag_config("success", foreground="#22c55e", font=('Consolas', 9, 'bold'))
        self.console.tag_config("fail", foreground="#ef4444")
        self.console.tag_config("info", foreground="#06b6d4")
        self.console.tag_config("warning", foreground="#f59e0b")
        
        self.console.config(state="disabled")
    
    def build_monitor_tab(self):
        container = ttk.Frame(self.tab_monitor)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        config_frame = ttk.Frame(container, style='Card.TFrame')
        config_frame.pack(fill=tk.X, pady=(0, 5))
        
        config_content = ttk.Frame(config_frame, padding=10)
        config_content.pack(fill=tk.X)
        
        ttk.Label(
            config_content,
            text="MONITOR CONFIGURATION",
            font=('Segoe UI', 11, 'bold')
        ).pack(anchor='w', pady=(0, 15))
        
        ttk.Label(
            config_content,
            text="Target Username",
            font=('Segoe UI', 10, 'bold')
        ).pack(anchor='w', pady=(0, 8))
        
        self.monitor_target_entry = ttk.Entry(config_content, takefocus=False)
        self.monitor_target_entry.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(
            config_content,
            text="Check Interval (seconds)",
            font=('Segoe UI', 10, 'bold')
        ).pack(anchor='w', pady=(0, 8))
        
        self.monitor_interval_entry = ttk.Entry(config_content, takefocus=False)
        self.monitor_interval_entry.pack(fill=tk.X, pady=(0, 20))
        self.monitor_interval_entry.insert(0, "60")
        
        self.monitor_btn = ttk.Button(
            config_content,
            text="Start monitor",
            command=self.start_monitor,
            style='Accent.TButton'
        )
        self.monitor_btn.pack(fill=tk.X)
        log_frame = ttk.Frame(container, style='Card.TFrame')
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        log_content = ttk.Frame(log_frame, padding=8)
        log_content.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            log_content,
            text="MONITOR LOG",
            font=('Segoe UI', 10, 'bold')
        ).pack(anchor='w', pady=(0, 5))
        
        log_scroll_frame = ttk.Frame(log_content)
        log_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        self.monitor_console = tk.Text(log_scroll_frame, wrap=tk.WORD, height=6, font=('Consolas', 8),
                                      bg='#1c1c1c', fg='#ffffff', insertbackground='#ffffff',
                                      relief='flat', borderwidth=0, highlightthickness=0, takefocus=0)
        scrollbar = ttk.Scrollbar(log_scroll_frame, command=self.monitor_console.yview)
        self.monitor_console.configure(yscrollcommand=scrollbar.set)
        
        self.monitor_console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.monitor_console.config(state="disabled")
    
    def build_proxies_tab(self):
        container = ttk.Frame(self.tab_proxies)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.proxy_mgr = ProxyManager()
        proxy_frame = ttk.Frame(container, style='Card.TFrame')
        proxy_frame.pack(fill=tk.BOTH, expand=True)
        
        proxy_content = ttk.Frame(proxy_frame, padding=8)
        proxy_content.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            proxy_content,
            text="PROXY MANAGER",
            font=('Segoe UI', 10, 'bold')
        ).pack(anchor='w', pady=(0, 8))
        
        tree_frame = ttk.Frame(proxy_content)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        columns = ('proxy', 'status', 'speed')
        self.proxy_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=6, takefocus=0)
        self.proxy_tree.heading('proxy', text='Proxy')
        self.proxy_tree.heading('status', text='Status')
        self.proxy_tree.heading('speed', text='Speed')
        self.proxy_tree.column('proxy', width=400)
        self.proxy_tree.column('status', width=100)
        self.proxy_tree.column('speed', width=80)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.proxy_tree.yview)
        self.proxy_tree.configure(yscroll=scrollbar.set)
        self.proxy_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.proxy_tree.tag_configure('good', foreground='#00ff00')
        self.proxy_tree.tag_configure('bad', foreground='#ff0000')
        add_frame = ttk.Frame(proxy_content)
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.proxy_entry = ttk.Entry(add_frame, takefocus=False)
        self.proxy_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.proxy_entry.insert(0, "host:port or user:pass@host:port")
        
        ttk.Button(
            add_frame,
            text="Add",
            command=self.add_proxy,
            style='Accent.TButton'
        ).pack(side=tk.LEFT)
        
        actions = ttk.Frame(proxy_content)
        actions.pack(fill=tk.X)
        
        ttk.Button(
            actions,
            text="Remove",
            command=self.remove_proxy
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            actions,
            text="Check all",
            command=self.check_proxies,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            actions,
            text="Remove bad",
            command=self.remove_bad_proxies
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            actions,
            text="Export",
            command=self.export_proxies
        ).pack(side=tk.LEFT, padx=2)
        
        self.proxy_stats_label = ttk.Label(
            proxy_content,
            text="Total: 0 | Good: 0 | Bad: 0",
            font=('Segoe UI', 9, 'bold')
        )
        self.proxy_stats_label.pack(pady=(10, 0))
        
        self.refresh_proxy_list()
    
    def build_settings_tab(self):
        container = ttk.Frame(self.tab_settings)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        general_frame = ttk.Frame(container, style='Card.TFrame')
        general_frame.pack(fill=tk.X, pady=(0, 20))
        
        general_content = ttk.Frame(general_frame, padding=20)
        general_content.pack(fill=tk.X)
        
        ttk.Label(
            general_content,
            text="GENERAL SETTINGS",
            font=('Segoe UI', 11, 'bold')
        ).pack(anchor='w', pady=(0, 15))
        
        ttk.Label(
            general_content,
            text="Thread Count (Concurrent Checks)",
            font=('Segoe UI', 10, 'bold')
        ).pack(anchor='w', pady=(0, 8))
        
        self.threads_entry = ttk.Entry(general_content, takefocus=False)
        self.threads_entry.pack(fill=tk.X, pady=(0, 20))
        self.threads_entry.insert(0, str(settings.get("threads", 10)))
        
        ttk.Checkbutton(
            general_content,
            text="Enable desktop notifications",
            variable=self.desktop_notifications,
            style='Switch.TCheckbutton'
        ).pack(anchor='w', pady=10)
        
        ttk.Separator(general_content, orient='horizontal').pack(fill=tk.X, pady=20)
        
        ttk.Label(
            general_content,
            text="Application Theme",
            font=('Segoe UI', 10, 'bold')
        ).pack(anchor='w', pady=(0, 8))
        
        theme_frame = ttk.Frame(general_content)
        theme_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.theme_var = tk.StringVar(value=self.theme_manager.get_current_theme())
        
        theme_names = [config['name'] for config in self.theme_manager.THEMES.values()]
        theme_keys = list(self.theme_manager.THEMES.keys())
        
        self.theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=theme_keys,
            state='readonly',
            width=30,
            takefocus=False
        )
        self.theme_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.theme_combo.bind('<<ComboboxSelected>>', self.change_theme)
        
        ttk.Button(
            theme_frame,
            text="Toggle Dark/Light",
            command=self.toggle_theme_mode
        ).pack(side=tk.LEFT)
        ttk.Button(
            general_content,
            text="Save settings",
            command=self.save_settings,
            style='Accent.TButton'
        ).pack(fill=tk.X, pady=(20, 0))
    
    def build_webhook_tab(self):
        container = ttk.Frame(self.tab_webhook)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        webhook_frame = ttk.Frame(container, style='Card.TFrame')
        webhook_frame.pack(fill=tk.X, pady=(0, 20))
        
        webhook_content = ttk.Frame(webhook_frame, padding=20)
        webhook_content.pack(fill=tk.X)
        
        ttk.Label(
            webhook_content,
            text="DISCORD WEBHOOK",
            font=('Segoe UI', 11, 'bold')
        ).pack(anchor='w', pady=(0, 15))
        
        ttk.Label(
            webhook_content,
            text="Discord Webhook URL",
            font=('Segoe UI', 10, 'bold')
        ).pack(anchor='w', pady=(0, 8))
        
        self.webhook_entry = ttk.Entry(webhook_content, takefocus=True, state="normal")
        self.webhook_entry.pack(fill=tk.X, pady=(0, 10))
        self.webhook_entry.configure(cursor="xterm")
        self.webhook_entry.bind("<Button-1>", lambda e: (self.webhook_entry.focus_force(), "break"))
        self.webhook_entry.bind("<FocusIn>", lambda e: self.webhook_entry.icursor(tk.END))
        self.webhook_entry.bind("<FocusIn>", lambda e: self.webhook_entry.configure(state="normal"), add="+")
        self.webhook_entry.insert(0, "https://discord.com/api/webhooks/...")
        current_webhook = settings.get("webhook_url", "")
        if current_webhook:
            self.webhook_entry.delete(0, tk.END)
            self.webhook_entry.insert(0, current_webhook)
        
        ttk.Label(
            webhook_content,
            text="Send notifications when available usernames are found",
            font=('Segoe UI', 9),
            foreground='gray'
        ).pack(anchor='w')
        
        ttk.Button(
            webhook_content,
            text="Save webhook",
            command=self.save_settings,
            style='Accent.TButton'
        ).pack(fill=tk.X, pady=(15, 0))
        ttk.Button(
            webhook_content,
            text="Test webhook",
            command=self.test_webhook,
            style='Accent.TButton'
        ).pack(fill=tk.X, pady=(6, 0))

    def build_about_tab(self):
        container = ttk.Frame(self.tab_about)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        about_frame = ttk.Frame(container, style='Card.TFrame')
        about_frame.pack(fill=tk.X)
        
        about_content = ttk.Frame(about_frame, padding=20)
        about_content.pack(fill=tk.X)
        
        ttk.Label(
            about_content,
            text="ABOUT",
            font=('Segoe UI', 11, 'bold')
        ).pack(anchor='w', pady=(0, 15))
        
        ttk.Label(
            about_content,
            text="Username Checker v1.0.2",
            font=('Segoe UI', 12, 'bold')
        ).pack(anchor='w')
        
        ttk.Label(
            about_content,
            text="A modern tool for checking username availability across multiple platforms.",
            font=('Segoe UI', 9),
            wraplength=800,
            justify=tk.LEFT
        ).pack(anchor='w', pady=(5, 15))
        
        ttk.Label(
            about_content,
            text="Discord: tlwm",
            font=('Segoe UI', 9)
        ).pack(anchor='w')
        ttk.Label(
            about_content,
            text="Telegram: https://t.me/feicoes",
            font=('Segoe UI', 9)
        ).pack(anchor='w')
        ttk.Label(
            about_content,
            text="GitHub: https://github.com/00ie",
            font=('Segoe UI', 9)
        ).pack(anchor='w', pady=(0, 15))
        
        ttk.Label(
            about_content,
            text="Made by Gon",
            font=('Segoe UI', 9, 'bold')
        ).pack(anchor='w', pady=(0, 15))
        
        shortcuts_text = "Keyboard Shortcuts: Ctrl+G (Generate) | Ctrl+R (Run) | Ctrl+S (Export) | Ctrl+Q (Quit) | Ctrl+1/2/3/4/5/6 (Tabs) | F5 (Refresh)"
        ttk.Label(
            about_content,
            text=shortcuts_text,
            font=('Consolas', 8),
            wraplength=800,
            justify=tk.LEFT
        ).pack(anchor='w')
    
    def create_footer(self):
        footer = ttk.Frame(self.root, style='Card.TFrame')
        footer.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(0, 5))
        
        footer_content = ttk.Frame(footer, padding=5)
        footer_content.pack(fill=tk.X)
        self.status_label = ttk.Label(
            footer_content,
            text="System Ready",
            font=('Segoe UI', 8)
        )
        self.status_label.pack(side=tk.LEFT, padx=8)
        speed_frame = ttk.Frame(footer_content)
        speed_frame.pack(side=tk.LEFT, padx=8)
        
        ttk.Label(
            speed_frame,
            text="",
            font=('Segoe UI', 8)
        ).pack(side=tk.LEFT)
        
        ttk.Label(
            speed_frame,
            textvariable=self.stat_speed,
            font=('Segoe UI', 8)
        ).pack(side=tk.LEFT)
        
        ttk.Label(
            footer_content,
            text="v1.0.2",
            font=('Segoe UI', 7)
        ).pack(side=tk.RIGHT, padx=8)
    
    def generate_usernames(self):
        try:
            count_str = self.count_entry.get().strip()
            length_str = self.length_entry.get().strip()
            valid_count, count_error = InputValidator.validate_number(count_str, 1, 10000)
            if not valid_count:
                Toast.show(self.root, f"Invalid count: {count_error}", "error")
                return
            
            valid_length, length_error = InputValidator.validate_number(length_str, 2, 20)
            if not valid_length:
                Toast.show(self.root, f"Invalid length: {length_error}", "error")
                return
            
            count = int(count_str)
            length = int(length_str)
            
            self.targets = []
            chars = string.ascii_lowercase + string.digits
            
            for _ in range(count):
                username = "".join(random.choices(chars, k=length))
                self.targets.append(username)
            
            self._log_to_console(f"Generated {len(self.targets)} usernames", "success")
            Toast.show(self.root, f"Generated {len(self.targets)} usernames", "success")
            
        except Exception as e:
            Toast.show(self.root, f"Error generating usernames: {str(e)}", "error")
    
    def import_usernames(self):
        file_path = filedialog.askopenfilename(
            title="Select username file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                usernames = [line.strip() for line in f if line.strip()]
            
            self.targets = usernames
            self._log_to_console(f"Imported {len(usernames)} usernames from file", "success")
            Toast.show(self.root, f"Imported {len(usernames)} usernames", "success")
            
        except Exception as e:
            Toast.show(self.root, f"Error importing file: {str(e)}", "error")
    
    def start_bulk(self):
        if not self.targets:
            Toast.show(self.root, "No usernames to check! Generate or import first.", "warning")
            return
        self.save_config()
        self.stat_total.set(0)
        self.stat_avail.set(0)
        self.results_cache.clear()
        self.start_time = datetime.now().timestamp()
        self.bulk_start_btn.config(state='disabled')
        self.status_label.config(text="Bulk check running...")
        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = len(self.targets)
        thread = threading.Thread(target=self.run_bulk_check, daemon=True)
        thread.start()
    
    def run_bulk_check(self):
        self.engine.start_bulk(self.targets, self.handle_check_result)
        self.root.after(0, self.finish_bulk_check)
    
    def handle_check_result(self, data: Dict[str, Any]):
        self.root.after(0, lambda: self._update_stats(data))
        username = data['username']
        timestamp = data['timestamp']
        
        if data['available_on']:
            self.results_cache.append(data)
            platforms = ", ".join([p.upper() for p in data['available_on']])
            db.save_check_result(
                username,
                data['checked_platforms'],
                data['available_on'],
                self.session_id
            )
            
            message = f"[{timestamp}] {username:<15} | Available on: {platforms}"
            self.root.after(0, lambda m=message: self._log_to_console(m, "success"))
            
            if self.desktop_notifications.get():
                notification_manager.notify_username_available(username, data['available_on'])
            if self.auto_export.get():
                self.quick_export_available()
        else:
            if not self.hide_taken.get():
                message = f"[{timestamp}] {username:<15} | Taken"
                self.root.after(0, lambda m=message: self._log_to_console(m, "fail"))
            db.save_check_result(
                username,
                data['checked_platforms'],
                [],
                self.session_id
            )
    
    def _update_stats(self, data: Dict[str, Any]):
        new_total = self.stat_total.get() + 1
        self.stat_total.set(new_total)
        if data['available_on']:
            new_avail = self.stat_avail.get() + 1
            self.stat_avail.set(new_avail)
        if new_total > 0:
            rate = (self.stat_avail.get() / new_total) * 100
            self.stat_rate.set(f"{rate:.1f}%")
        self.progress_bar['value'] = new_total
        if len(self.targets) > 0:
            percent = (new_total / len(self.targets)) * 100
            self.progress_percent.config(text=f"{percent:.0f}%")
            self.progress_label.config(text=f"Checking... {new_total}/{len(self.targets)}")
        
        if self.start_time:
            elapsed = datetime.now().timestamp() - self.start_time
            if elapsed > 0:
                speed = new_total / elapsed
                self.stat_speed.set(f"{speed:.1f}/s")
        db.update_session_stats(self.session_id, new_total, self.stat_avail.get())
    
    def finish_bulk_check(self):
        self.bulk_start_btn.config(state='normal')
        self.status_label.config(text="Check complete!")
        self.progress_label.config(text="Check complete!")
        self.progress_percent.config(text="100%")
        
        message = f"\nBulk check completed! Found {self.stat_avail.get()} available usernames out of {self.stat_total.get()} checked."
        self._log_to_console(message, "success")
        
        Toast.show(
            self.root,
            f"Found {self.stat_avail.get()} available usernames!",
            "success",
            5000
        )
        
        db.end_session(self.session_id)
    
    def stop_audit(self):
        self.engine.stop()
        self.bulk_start_btn.config(state='normal')
        self.monitor_btn.config(state='normal', text="Activate Monitor")
        self.status_label.config(text="Stopped")
        Toast.show(self.root, "Audit stopped", "info")
        self._log_to_console("Audit stopped by user", "warning")
    
    def start_monitor(self):
        target = self.monitor_target_entry.get().strip()
        
        if target == "username":
            target = ""
        
        if not target:
            Toast.show(self.root, "Please enter a username to monitor", "warning")
            return
        
        valid, error = InputValidator.validate_username(target)
        if not valid:
            Toast.show(self.root, f"Invalid username: {error}", "error")
            return
        try:
            interval = int(self.monitor_interval_entry.get())
            if interval < 5:
                Toast.show(self.root, "Interval must be at least 5 seconds", "warning")
                return
        except ValueError:
            Toast.show(self.root, "Invalid interval", "error")
            return
        self.save_config()
        self.monitor_btn.config(state='disabled', text="Monitoring...")
        self.status_label.config(text=f"Monitoring @{target}")
        thread = threading.Thread(
            target=lambda: self.engine.start_monitor(target, self.handle_monitor_result, interval),
            daemon=True
        )
        thread.start()
        
        self._log_to_monitor(f"Started monitoring @{target} (every {interval}s)", "info")
        Toast.show(self.root, f"Monitoring @{target}", "info")
    
    def handle_monitor_result(self, data: Dict[str, Any]):
        timestamp = data['timestamp']
        username = data['username']
        
        if data['available_on']:
            platforms = ", ".join([p.upper() for p in data['available_on']])
            message = f"[{timestamp}] @{username} is available on: {platforms}!"
            
            self.root.after(0, lambda m=message: self._log_to_monitor(m, "success"))
            
            if self.desktop_notifications.get():
                notification_manager.notify_username_available(username, data['available_on'])
            
            Toast.show(self.root, f"@{username} is available!", "success", 10000)
        else:
            message = f"[{timestamp}] Still taken..."
            self.root.after(0, lambda m=message: self._log_to_monitor(m, "fail"))
    
    def export_results(self):
        if not self.results_cache:
            Toast.show(self.root, "No results to export", "warning")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("CSV files", "*.csv"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.csv':
                self._export_csv(file_path)
            elif ext == '.json':
                self._export_json(file_path)
            else:
                self._export_txt(file_path)
            
            Toast.show(self.root, f"Exported {len(self.results_cache)} results", "success")
            self._log_to_console(f"Exported to {file_path}", "success")
            
        except Exception as e:
            Toast.show(self.root, f"Export failed: {str(e)}", "error")
    
    def _export_txt(self, file_path: str):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("USERNAME CHECKER - AVAILABLE USERNAMES\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            for item in self.results_cache:
                platforms = ", ".join([p.upper() for p in item['available_on']])
                f.write(f"Username: @{item['username']}\n")
                f.write(f"Platforms: {platforms}\n")
                f.write(f"Timestamp: {item['timestamp']}\n")
                f.write("-" * 60 + "\n")
    
    def _export_csv(self, file_path: str):
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Username', 'Platforms', 'Timestamp'])
            
            for item in self.results_cache:
                platforms = ", ".join(item['available_on'])
                writer.writerow([item['username'], platforms, item['timestamp']])
    
    def _export_json(self, file_path: str):
        export_data = {
            'generated_at': datetime.now().isoformat(),
            'total_available': len(self.results_cache),
            'session_id': self.session_id,
            'results': self.results_cache
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
    
    def quick_export_available(self):
        try:
            os.makedirs('exports', exist_ok=True)
            filename = f"exports/available_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                for item in self.results_cache:
                    platforms = ", ".join(item['available_on'])
                    f.write(f"{item['username']} | {platforms}\n")
        except Exception:
            pass
    
    def refresh_proxy_list(self):
        for item in self.proxy_tree.get_children():
            self.proxy_tree.delete(item)
        
        proxies = list(self.proxy_mgr.proxies)
        good_count = 0
        bad_count = 0
        
        for proxy in proxies:
            is_bad = self.proxy_mgr.is_blacklisted(proxy)
            status = "BAD" if is_bad else "OK"
            tag = 'bad' if is_bad else 'good'
            
            if is_bad:
                bad_count += 1
            else:
                good_count += 1
            
            self.proxy_tree.insert('', 'end', values=(proxy, status, "-"), tags=(tag,))
        
        total = len(proxies)
        self.proxy_stats_label.config(
            text=f"Total: {total} | Good: {good_count} | Bad: {bad_count}"
        )
    
    def add_proxy(self):
        proxy_str = self.proxy_entry.get().strip()
        
        if "host:port" in proxy_str or not proxy_str:
            Toast.show(self.root, "Please enter a valid proxy", "warning")
            return
        valid, error = InputValidator.validate_proxy(proxy_str)
        if not valid:
            Toast.show(self.root, f"Invalid proxy: {error}", "error")
            return
        if self.proxy_mgr.add_proxy(proxy_str):
            self.proxy_entry.delete(0, tk.END)
            self.refresh_proxy_list()
            Toast.show(self.root, "Proxy added", "success")
        else:
            Toast.show(self.root, "Proxy already exists", "warning")
    
    def remove_proxy(self):
        selection = self.proxy_tree.selection()
        if not selection:
            Toast.show(self.root, "No proxy selected", "warning")
            return
        
        item = self.proxy_tree.item(selection[0])
        proxy = item['values'][0]
        
        if self.proxy_mgr.remove_proxy(proxy):
            self.refresh_proxy_list()
            Toast.show(self.root, "Proxy removed", "success")
    
    def check_proxies(self):
        proxies = list(self.proxy_mgr.proxies)
        
        if not proxies:
            Toast.show(self.root, "No proxies to check", "warning")
            return
        
        Toast.show(self.root, f"Checking {len(proxies)} proxies...", "info")
        
        def worker():
            results = check_proxies(proxies, workers=min(50, max(5, len(proxies))))
            ok = sum(1 for r in results if r[1])
            bad = len(results) - ok
            
            self.root.after(0, lambda: Toast.show(
                self.root,
                f"Check complete! OK: {ok} | Bad: {bad}",
                "success"
            ))
            
            self.proxy_mgr.load_blacklist()
            self.root.after(0, self.refresh_proxy_list)
        
        threading.Thread(target=worker, daemon=True).start()
    
    def remove_bad_proxies(self):
        bad = [p for p in self.proxy_mgr.proxies if self.proxy_mgr.is_blacklisted(p)]
        
        if not bad:
            Toast.show(self.root, "No bad proxies to remove", "info")
            return
        
        if not messagebox.askyesno("Confirm", f"Remove {len(bad)} bad proxies?"):
            return
        
        for proxy in bad:
            self.proxy_mgr.remove_proxy(proxy)
        
        self.refresh_proxy_list()
        Toast.show(self.root, f"Removed {len(bad)} bad proxies", "success")
    
    def export_proxies(self):
        try:
            good = [p for p in self.proxy_mgr.proxies if not self.proxy_mgr.is_blacklisted(p)]
            bad = [p for p in self.proxy_mgr.proxies if self.proxy_mgr.is_blacklisted(p)]
            
            os.makedirs('exports', exist_ok=True)
            
            with open('exports/good_proxies.txt', 'w') as f:
                f.write('\n'.join(good))
            
            with open('exports/bad_proxies.txt', 'w') as f:
                f.write('\n'.join(bad))
            
            Toast.show(self.root, f"Exported {len(good)} good and {len(bad)} bad proxies", "success")
        except Exception as e:
            Toast.show(self.root, f"Export failed: {str(e)}", "error")
    
    def save_config(self):
        for platform, var in self.platform_vars.items():
            settings.set(f"platforms.{platform}", var.get())
        
        settings.set("use_proxies", self.use_proxies.get())
        settings.save()
        self.engine.refresh_settings()
    
    def save_settings(self):
        webhook = self.webhook_entry.get().strip() if hasattr(self, 'webhook_entry') else ""
        if webhook and webhook != "https://discord.com/api/webhooks/...":
            valid, error = InputValidator.validate_url(webhook)
            if not valid:
                Toast.show(self.root, f"Invalid webhook URL: {error}", "error")
                return
            settings.set("webhook_url", webhook)
        else:
            settings.set("webhook_url", "")
        
        threads_str = self.threads_entry.get().strip() if hasattr(self, 'threads_entry') else "10"
        valid, error = InputValidator.validate_number(threads_str, 1, 100)
        if not valid:
            Toast.show(self.root, f"Invalid thread count: {error}", "error")
            return
        settings.set("threads", int(threads_str))
        
        settings.set("theme", self.theme_manager.get_current_theme())
        
        settings.save()
        self.engine.refresh_settings()
        Toast.show(self.root, "Settings saved successfully!", "success")

    def test_webhook(self):
        webhook = self.webhook_entry.get().strip() if hasattr(self, 'webhook_entry') else ""
        if not webhook or webhook == "https://discord.com/api/webhooks/...":
            Toast.show(self.root, "Please enter a webhook URL", "warning")
            return
        valid, error = InputValidator.validate_url(webhook)
        if not valid:
            Toast.show(self.root, f"Invalid webhook URL: {error}", "error")
            return
        try:
            import requests
            payload = {
                "username": "Username Checker",
                "content": "Webhook test: your configuration is working."
            }
            response = requests.post(webhook, json=payload, timeout=8)
            if response.status_code >= 400:
                Toast.show(self.root, f"Webhook test failed ({response.status_code})", "error")
                return
            settings.set("webhook_url", webhook)
            settings.save()
            Toast.show(self.root, "Webhook test sent successfully!", "success")
        except Exception as exc:
            Toast.show(self.root, f"Webhook test failed: {exc}", "error")
    
    def change_theme(self, event=None):
        if hasattr(self, '_theme_changing') and self._theme_changing:
            return
        
        theme_key = self.theme_var.get()
        
        if theme_key == self.theme_manager.get_current_theme():
            return
        
        self._theme_changing = True
        
        if self.theme_manager.apply_theme(theme_key):
            Toast.show(self.root, f"Theme changed!", "success")
        
        self._theme_changing = False
    
    def toggle_theme_mode(self):
        if hasattr(self, '_theme_changing') and self._theme_changing:
            return
        
        self._theme_changing = True
        
        self.theme_manager.toggle_mode()
        self.theme_var.set(self.theme_manager.get_current_theme())
        
        self._theme_changing = False
        
        Toast.show(self.root, "Theme mode toggled!", "success")
    
    def get_enabled_platforms(self) -> List[str]:
        return [p for p, var in self.platform_vars.items() if var.get()]
    
    def auto_save(self):
        if self.results_cache and self.auto_export.get():
            self.quick_export_available()
        self.root.after(60000, self.auto_save)
    
    def refresh_ui(self):
        self.refresh_proxy_list()
        Toast.show(self.root, "UI refreshed", "info")
    
    def _log_to_console(self, message: str, tag: str = "info"):
        self.console.config(state="normal")
        self.console.insert("end", f"{message}\n", tag)
        self.console.see("end")
        self.console.config(state="disabled")
    
    def _log_to_monitor(self, message: str, tag: str = "info"):
        self.monitor_console.config(state="normal")
        self.monitor_console.insert("end", f"{message}\n", tag)
        self.monitor_console.see("end")
        self.monitor_console.config(state="disabled")
    
    def on_closing(self):
        if self.engine.active:
            if not messagebox.askyesno("Confirm Exit", "An audit is running. Are you sure you want to quit?"):
                return
        self.engine.stop()
        db.close()
        self.root.destroy()
    
    def run(self):
        
        self.root.deiconify()
        self.root.update_idletasks()
        
        self.root.mainloop()


MainWindow = AppWindow
