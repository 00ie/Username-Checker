import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Dict, Any, Optional
from gui.ui_components import ModernUI


class Toast(tk.Toplevel):
    
    def __init__(self, parent: tk.Widget, message: str, type_: str = "info", duration: int = 3000):
        super().__init__(parent)
        
        self.wm_overrideredirect(True)
        self.attributes('-topmost', True)
        
        colors = {
            'success': ModernUI.SUCCESS,
            'error': ModernUI.ERROR,
            'warning': ModernUI.WARNING,
            'info': ModernUI.INFO
        }
        color = colors.get(type_, colors['info'])
        
        frame = tk.Frame(self, bg=ModernUI.BG_SEC, highlightthickness=1,
                        highlightbackground=color)
        frame.pack(padx=2, pady=2)
        
        content = tk.Frame(frame, bg=ModernUI.BG_SEC)
        content.pack(padx=15, pady=10)
        
        tk.Label(
            content,
            text=message,
            bg=ModernUI.BG_SEC,
            fg=ModernUI.FG,
            font=('Segoe UI', 9)
        ).pack()
        
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        x = screen_width - width - 20
        y = screen_height - height - 60
        
        self.geometry(f"+{x}+{y}")
        
        self.after(duration, self.destroy)
    
    @staticmethod
    def show(parent: tk.Widget, message: str, type_: str = "info", duration: int = 3000):
        Toast(parent, message, type_, duration)


class SearchableConsole(tk.Frame):
    
    def __init__(self, parent: tk.Widget, **kwargs):
        super().__init__(parent, bg=ModernUI.BG)
        
        toolbar = tk.Frame(self, bg=ModernUI.BG_SEC, height=40)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search)
        
        search_frame = tk.Frame(toolbar, bg=ModernUI.BG_SEC)
        search_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        tk.Label(
            search_frame,
            text="Search",
            bg=ModernUI.BG_SEC,
            fg=ModernUI.FG_DIM,
            font=('Segoe UI', 10)
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            bg=ModernUI.BG,
            fg=ModernUI.FG,
            font=('Segoe UI', 9),
            relief=tk.FLAT,
            bd=5,
            width=25
        )
        search_entry.pack(side=tk.LEFT)
        
        self.filter_success = tk.BooleanVar(value=True)
        self.filter_error = tk.BooleanVar(value=True)
        self.filter_info = tk.BooleanVar(value=True)
        
        filter_frame = tk.Frame(toolbar, bg=ModernUI.BG_SEC)
        filter_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Checkbutton(
            filter_frame,
            text="Success",
            variable=self.filter_success,
            bg=ModernUI.BG_SEC,
            fg=ModernUI.SUCCESS,
            selectcolor=ModernUI.BG,
            activebackground=ModernUI.BG_SEC,
            font=('Segoe UI', 8),
            bd=0,
            command=self._apply_filters
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Checkbutton(
            filter_frame,
            text="Errors",
            variable=self.filter_error,
            bg=ModernUI.BG_SEC,
            fg=ModernUI.ERROR,
            selectcolor=ModernUI.BG,
            activebackground=ModernUI.BG_SEC,
            font=('Segoe UI', 8),
            bd=0,
            command=self._apply_filters
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Checkbutton(
            filter_frame,
            text="Info",
            variable=self.filter_info,
            bg=ModernUI.BG_SEC,
            fg=ModernUI.INFO,
            selectcolor=ModernUI.BG,
            activebackground=ModernUI.BG_SEC,
            font=('Segoe UI', 8),
            bd=0,
            command=self._apply_filters
        ).pack(side=tk.LEFT, padx=5)
        
        actions = tk.Frame(toolbar, bg=ModernUI.BG_SEC)
        actions.pack(side=tk.RIGHT, padx=10)
        
        ModernUI.button(
            actions,
            "Clear",
            self.clear,
            danger=True
        ).pack(side=tk.LEFT, padx=2)
        
        ModernUI.button(
            actions,
            "Copy",
            self._copy_to_clipboard
        ).pack(side=tk.LEFT, padx=2)
        
        self.console = ModernUI.console(self)
        self.console.pack(fill=tk.BOTH, expand=True)
        
        self.all_logs: List[tuple] = []
    
    def log(self, message: str, tag: str = "info"):
        self.all_logs.append((message, tag))
        
        if self._should_show_log(tag):
            self.console.config(state="normal")
            self.console.insert("end", f"{message}\n", tag)
            self.console.see("end")
            self.console.config(state="disabled")
    
    def clear(self):
        self.console.config(state="normal")
        self.console.delete(1.0, "end")
        self.console.config(state="disabled")
        self.all_logs.clear()
    
    def _should_show_log(self, tag: str) -> bool:
        if tag == "success" and not self.filter_success.get():
            return False
        if tag == "fail" and not self.filter_error.get():
            return False
        if tag == "info" and not self.filter_info.get():
            return False
        return True
    
    def _apply_filters(self):
        self.console.config(state="normal")
        self.console.delete(1.0, "end")
        
        for message, tag in self.all_logs:
            if self._should_show_log(tag):
                self.console.insert("end", f"{message}\n", tag)
        
        self.console.config(state="disabled")
    
    def _on_search(self, *args):
        search_term = self.search_var.get().lower()
        
        if not search_term:
            self.console.tag_remove("highlight", "1.0", "end")
            return
        
        self.console.tag_remove("highlight", "1.0", "end")
        
        start = "1.0"
        while True:
            pos = self.console.search(search_term, start, stopindex="end", nocase=True)
            if not pos:
                break
            
            end = f"{pos}+{len(search_term)}c"
            self.console.tag_add("highlight", pos, end)
            start = end
    
    def _copy_to_clipboard(self):
        content = self.console.get(1.0, "end-1c")
        self.clipboard_clear()
        self.clipboard_append(content)
        Toast.show(self, "Copied to clipboard!", "success", 2000)


class EnhancedTreeview(tk.Frame):
    
    def __init__(self, parent: tk.Widget, columns: List[tuple], **kwargs):
        super().__init__(parent, bg=ModernUI.BG)
        
        search_frame = tk.Frame(self, bg=ModernUI.BG)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._filter_items)
        
        tk.Label(
            search_frame,
            text="Search",
            bg=ModernUI.BG,
            fg=ModernUI.FG_DIM
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ModernUI.entry(search_frame, placeholder="Search...").pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        self.search_entry = list(search_frame.children.values())[-1]
        self.search_entry.config(textvariable=self.search_var)
        
        self.columns = columns
        column_ids = [col[0] for col in columns]
        
        self.tree = ttk.Treeview(self, columns=column_ids, show='headings', **kwargs)
        
        for col_id, col_name, width in columns:
            self.tree.heading(col_id, text=col_name, command=lambda c=col_id: self._sort_by(c))
            self.tree.column(col_id, width=width)
        
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        style = ttk.Style()
        style.configure(
            "Treeview",
            background=ModernUI.BG,
            foreground=ModernUI.FG,
            fieldbackground=ModernUI.BG,
            borderwidth=0
        )
        style.configure("Treeview.Heading", background=ModernUI.BG_SEC, foreground=ModernUI.FG)
        style.map('Treeview', background=[('selected', ModernUI.ACCENT)])
        
        self.all_items: List[tuple] = []
        self.sort_reverse = False
        self.sort_column = None
    
    def insert_item(self, values: tuple, tags: tuple = ()):
        self.all_items.append((values, tags))
        self.tree.insert('', 'end', values=values, tags=tags)
    
    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.all_items.clear()
    
    def _sort_by(self, column: str):
        self.sort_reverse = not self.sort_reverse if self.sort_column == column else False
        self.sort_column = column
        
        col_idx = [col[0] for col in self.columns].index(column)
        
        sorted_items = sorted(
            self.all_items,
            key=lambda x: x[0][col_idx],
            reverse=self.sort_reverse
        )
        
        self.tree.delete(*self.tree.get_children())
        for values, tags in sorted_items:
            self.tree.insert('', 'end', values=values, tags=tags)
    
    def _filter_items(self, *args):
        search_term = self.search_var.get().lower()
        
        self.tree.delete(*self.tree.get_children())
        
        for values, tags in self.all_items:
            if not search_term or any(search_term in str(v).lower() for v in values):
                self.tree.insert('', 'end', values=values, tags=tags)


class LoadingSpinner(tk.Label):
    
    FRAMES = ["", ".", "..", "..."]
    
    def __init__(self, parent: tk.Widget, text: str = "Loading", **kwargs):
        super().__init__(
            parent,
            text=f"{text}{self.FRAMES[0]}",
            bg=ModernUI.BG,
            fg=ModernUI.ACCENT,
            font=('Segoe UI', 10),
            **kwargs
        )
        
        self.base_text = text
        self.frame_idx = 0
        self.animating = False
        self.animation_id = None
    
    def start(self):
        self.animating = True
        self._animate()
    
    def stop(self):
        self.animating = False
        if self.animation_id:
            self.after_cancel(self.animation_id)
    
    def _animate(self):
        if not self.animating:
            return
        
        self.frame_idx = (self.frame_idx + 1) % len(self.FRAMES)
        self.config(text=f"{self.base_text}{self.FRAMES[self.frame_idx]}")
        
        self.animation_id = self.after(100, self._animate)
