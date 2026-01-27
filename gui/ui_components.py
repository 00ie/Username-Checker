import tkinter as tk
from tkinter import scrolledtext, ttk, font
from typing import Optional, Callable, Any


class ModernUI:
    BG = "#0f0f0f"
    BG_SEC = "#1a1a1a"
    BG_CARD = "#18181b"
    FG = "#f4f4f5"
    FG_SEC = "#a1a1aa"
    FG_DIM = "#71717a"
    
    ACCENT = "#3b82f6"
    ACCENT_HOVER = "#2563eb"
    ACCENT_LIGHT = "#60a5fa"
    
    SUCCESS = "#22c55e"
    SUCCESS_DIM = "#16a34a"
    ERROR = "#ef4444"
    ERROR_DIM = "#dc2626"
    WARNING = "#f59e0b"
    INFO = "#06b6d4"
    
    BORDER = "#27272a"
    BORDER_LIGHT = "#3f3f46"
    
    SHADOW_SM = "#0a0a0a"
    SHADOW_MD = "#050505"
    
    @staticmethod
    def create_card(parent: tk.Widget, title: Optional[str] = None, **kwargs) -> tk.Frame:
        shadow_frame = tk.Frame(parent, bg=ModernUI.SHADOW_MD, **kwargs)
        card = tk.Frame(shadow_frame, bg=ModernUI.BG_CARD, highlightthickness=1, 
                       highlightbackground=ModernUI.BORDER)
        card.pack(padx=2, pady=2, fill=tk.BOTH, expand=True)
        
        if title:
            header = tk.Frame(card, bg=ModernUI.BG_CARD, height=40)
            header.pack(fill=tk.X, padx=15, pady=(12, 8))
            header.pack_propagate(False)
            
            tk.Label(
                header, 
                text=title, 
                bg=ModernUI.BG_CARD, 
                fg=ModernUI.FG,
                font=('Segoe UI', 11, 'bold')
            ).pack(side=tk.LEFT, anchor='w')
        
        return card
    
    @staticmethod
    def button(parent: tk.Widget, text: str, command: Optional[Callable] = None, 
               icon: str = "", primary: bool = False, danger: bool = False, 
               success: bool = False, **kwargs) -> tk.Button:
        if primary:
            bg, hover_bg = ModernUI.ACCENT, ModernUI.ACCENT_HOVER
        elif danger:
            bg, hover_bg = ModernUI.ERROR, ModernUI.ERROR_DIM
        elif success:
            bg, hover_bg = ModernUI.SUCCESS, ModernUI.SUCCESS_DIM
        else:
            bg, hover_bg = ModernUI.BG_SEC, ModernUI.BORDER_LIGHT
        
        fg = ModernUI.FG
        
        display_text = f"{icon} {text}" if icon else text
        
        btn = tk.Button(
            parent,
            text=display_text,
            command=command,
            bg=bg,
            fg=fg,
            font=('Segoe UI', 9, 'bold'),
            relief=tk.FLAT,
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2",
            activebackground=hover_bg,
            activeforeground=fg,
            **kwargs
        )
        
        def on_enter(e):
            btn['bg'] = hover_bg
        
        def on_leave(e):
            btn['bg'] = bg
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    @staticmethod
    def entry(parent: tk.Widget, placeholder: str = "", **kwargs) -> tk.Entry:
        entry = tk.Entry(
            parent,
            bg=ModernUI.BG,
            fg=ModernUI.FG,
            font=('Segoe UI', 10),
            relief=tk.FLAT,
            insertbackground=ModernUI.ACCENT,
            bd=0,
            highlightthickness=1,
            highlightcolor=ModernUI.ACCENT,
            highlightbackground=ModernUI.BORDER,
            **kwargs
        )
        
        if placeholder:
            entry.insert(0, placeholder)
            entry.config(fg=ModernUI.FG_DIM)
            
            def on_focus_in(e):
                if entry.get() == placeholder:
                    entry.delete(0, tk.END)
                    entry.config(fg=ModernUI.FG)
            
            def on_focus_out(e):
                if not entry.get():
                    entry.insert(0, placeholder)
                    entry.config(fg=ModernUI.FG_DIM)
            
            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)
        
        entry.config(bd=10)
        
        return entry
    
    @staticmethod
    def console(parent: tk.Widget, **kwargs) -> scrolledtext.ScrolledText:
        console = scrolledtext.ScrolledText(
            parent,
            bg=ModernUI.BG,
            fg=ModernUI.FG_SEC,
            font=('JetBrains Mono', 9) if 'JetBrains Mono' in font.families() else ('Consolas', 9),
            relief=tk.FLAT,
            padx=15,
            pady=15,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=ModernUI.BORDER,
            insertbackground=ModernUI.ACCENT,
            **kwargs
        )
        
        console.tag_config("success", foreground=ModernUI.SUCCESS, font=('Consolas', 9, 'bold'))
        console.tag_config("fail", foreground=ModernUI.ERROR)
        console.tag_config("info", foreground=ModernUI.INFO)
        console.tag_config("warning", foreground=ModernUI.WARNING)
        console.tag_config("timestamp", foreground=ModernUI.FG_DIM)
        console.tag_config("username", foreground=ModernUI.ACCENT_LIGHT, font=('Consolas', 9, 'bold'))
        console.tag_config("platform", foreground=ModernUI.SUCCESS)
        console.tag_config("highlight", background=ModernUI.BG_SEC)
        
        return console
    
    @staticmethod
    def checkbox(parent: tk.Widget, text: str, variable: tk.BooleanVar, 
                 icon_checked: str = "", icon_unchecked: str = "") -> tk.Checkbutton:
        cb = tk.Checkbutton(
            parent,
            text=f"  {text}",
            variable=variable,
            bg=ModernUI.BG_CARD,
            fg=ModernUI.FG,
            selectcolor=ModernUI.BG_SEC,
            activebackground=ModernUI.BG_CARD,
            activeforeground=ModernUI.FG,
            font=('Segoe UI', 9),
            bd=0,
            cursor="hand2",
            relief=tk.FLAT
        )
        
        return cb
    
    @staticmethod
    def progress_bar(parent: tk.Widget, **kwargs) -> ttk.Progressbar:
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Modern.Horizontal.TProgressbar",
            troughcolor=ModernUI.BG_SEC,
            background=ModernUI.ACCENT,
            bordercolor=ModernUI.BORDER,
            lightcolor=ModernUI.ACCENT_LIGHT,
            darkcolor=ModernUI.ACCENT_HOVER,
            borderwidth=0,
            thickness=8
        )
        
        progress = ttk.Progressbar(
            parent,
            style="Modern.Horizontal.TProgressbar",
            mode='determinate',
            **kwargs
        )
        
        return progress
    
    @staticmethod
    def tooltip(widget: tk.Widget, text: str):
        tooltip_window = None
        
        def show_tooltip(event):
            nonlocal tooltip_window
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            
            tooltip_window = tk.Toplevel(widget)
            tooltip_window.wm_overrideredirect(True)
            tooltip_window.wm_geometry(f"+{x}+{y}")
            
            label = tk.Label(
                tooltip_window,
                text=text,
                bg=ModernUI.BG_SEC,
                fg=ModernUI.FG,
                relief=tk.SOLID,
                borderwidth=1,
                font=('Segoe UI', 8),
                padx=8,
                pady=4
            )
            label.pack()
        
        def hide_tooltip(event):
            nonlocal tooltip_window
            if tooltip_window:
                tooltip_window.destroy()
                tooltip_window = None
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
    
    @staticmethod
    def separator(parent: tk.Widget, **kwargs) -> tk.Frame:
        return tk.Frame(parent, bg=ModernUI.BORDER, height=1, **kwargs)
    
    @staticmethod
    def stat_card(parent: tk.Widget, title: str, value: tk.IntVar, 
                  color: str, icon: str = "") -> tk.Frame:
        card = tk.Frame(parent, bg=ModernUI.BG_CARD, highlightthickness=1,
                       highlightbackground=ModernUI.BORDER)
        card.pack(side=tk.LEFT, padx=8)
        
        content = tk.Frame(card, bg=ModernUI.BG_CARD)
        content.pack(padx=15, pady=12)
        
        header = tk.Frame(content, bg=ModernUI.BG_CARD)
        header.pack(anchor='w')
        
        if icon:
            tk.Label(
                header,
                text=icon,
                bg=ModernUI.BG_CARD,
                fg=color,
                font=('Segoe UI', 12)
            ).pack(side=tk.LEFT, padx=(0, 6))
        
        tk.Label(
            header,
            text=title,
            bg=ModernUI.BG_CARD,
            fg=ModernUI.FG_DIM,
            font=('Segoe UI', 8, 'bold')
        ).pack(side=tk.LEFT)
        
        tk.Label(
            content,
            textvariable=value,
            bg=ModernUI.BG_CARD,
            fg=color,
            font=('Segoe UI', 18, 'bold')
        ).pack(anchor='w', pady=(4, 0))
        
        return card


UI = ModernUI
