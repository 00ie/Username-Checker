import tkinter as tk
from tkinter import scrolledtext, ttk

class UI:
    BG = "#18181b"
    BG_SEC = "#27272a"
    FG = "#e4e4e7"
    FG_SEC = "#a1a1aa"
    ACCENT = "#3b82f6"
    ACCENT_HOVER = "#2563eb"
    SUCCESS = "#22c55e"
    ERROR = "#ef4444"
    BORDER = "#3f3f46"

    @staticmethod
    def button(parent, text, command, primary=False):
        bg = UI.ACCENT if primary else UI.BG_SEC
        fg = "#ffffff"
        
        btn = tk.Button(
            parent, text=text, command=command,
            bg=bg, fg=fg, font=('Segoe UI', 9, 'bold'),
            relief=tk.FLAT, bd=0, padx=20, pady=10,
            cursor="hand2", activebackground=fg, activeforeground=bg
        )
        
        def on_enter(e):
            btn['bg'] = UI.ACCENT_HOVER if primary else "#3f3f46"
        def on_leave(e):
            btn['bg'] = bg
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    @staticmethod
    def entry(parent):
        return tk.Entry(
            parent, bg="#09090b", fg=UI.FG,
            font=('Consolas', 10), relief=tk.FLAT,
            insertbackground="#ffffff", bd=8
        )

    @staticmethod
    def console(parent):
        area = scrolledtext.ScrolledText(
            parent, bg="#09090b", fg="#71717a",
            font=('Consolas', 9), relief=tk.FLAT,
            padx=15, pady=15, borderwidth=0, highlightthickness=0
        )
        area.tag_config("success", foreground=UI.SUCCESS)
        area.tag_config("fail", foreground=UI.ERROR)
        area.tag_config("info", foreground=UI.ACCENT)
        return area

    @staticmethod
    def checkbox(parent, text, variable):
        return tk.Checkbutton(
            parent, text=text, variable=variable,
            bg=UI.BG, fg=UI.FG, selectcolor=UI.BG_SEC,
            activebackground=UI.BG, activeforeground=UI.FG,
            font=('Segoe UI', 9), bd=0, cursor="hand2"
        )
        
    @staticmethod
    def label_frame(parent, text):
        return tk.LabelFrame(
            parent, text=text, bg=UI.BG, fg=UI.FG_SEC,
            font=('Segoe UI', 8, 'bold'), bd=1, relief=tk.SOLID,
            labelanchor="nw"
        )
