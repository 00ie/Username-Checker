import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import random
import string
import os
from datetime import datetime
from gui.components import UI
from core.engine import AuditEngine
from config.settings import settings

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Username Checker")
        self.root.geometry("1200x800")
        self.root.configure(bg=UI.BG)
        
        self.load_icon()
        self.engine = AuditEngine()
        self.targets = []
        self.results_cache = []
        
        self.stat_total = tk.IntVar(value=0)
        self.stat_avail = tk.IntVar(value=0)
        self.hide_taken = tk.BooleanVar(value=False)
        
        self.setup_layout()
        
    def load_icon(self):
        paths = ["icon.jpg", "assets/icon.jpg", "image.jpg"]
        for path in paths:
            if os.path.exists(path):
                try:
                    self.root.iconphoto(False, tk.PhotoImage(file=path))
                    break
                except: pass

    def setup_layout(self):
        header = tk.Frame(self.root, bg=UI.BG_SEC, height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="USERNAME CHECKER", bg=UI.BG_SEC, fg="#ffffff", font=('Segoe UI', 16, 'bold')).pack(side=tk.LEFT, padx=25)
        
        stats_frame = tk.Frame(header, bg=UI.BG_SEC)
        stats_frame.pack(side=tk.RIGHT, padx=25)
        
        self.create_stat_box(stats_frame, "CHECKED", self.stat_total, "#a1a1aa")
        self.create_stat_box(stats_frame, "AVAILABLE", self.stat_avail, UI.SUCCESS)
        
        body = tk.Frame(self.root, bg=UI.BG)
        body.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=UI.BG, borderwidth=0)
        style.configure('TNotebook.Tab', background=UI.BG_SEC, foreground=UI.FG, padding=[15, 5], font=('Segoe UI', 9))
        style.map('TNotebook.Tab', background=[('selected', UI.ACCENT)], foreground=[('selected', '#ffffff')])
        
        tab_control = ttk.Notebook(body)
        
        self.tab_bulk = tk.Frame(tab_control, bg=UI.BG)
        self.tab_monitor = tk.Frame(tab_control, bg=UI.BG)
        
        tab_control.add(self.tab_bulk, text='BULK CHECKER')
        tab_control.add(self.tab_monitor, text='SNIPER MONITOR')
        tab_control.pack(expand=1, fill="both")

        self.setup_bulk_tab()
        self.setup_monitor_tab()

        footer = tk.Frame(self.root, bg=UI.BG_SEC, height=35)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        self.status = tk.Label(footer, text="SYSTEM READY", bg=UI.BG_SEC, fg=UI.ACCENT, font=('Segoe UI', 8, 'bold'))
        self.status.pack(side=tk.LEFT, padx=15)
        tk.Label(footer, text="v1.0.0", bg=UI.BG_SEC, fg="#52525b", font=('Segoe UI', 8)).pack(side=tk.RIGHT, padx=15)

    def create_stat_box(self, parent, title, var, color):
        f = tk.Frame(parent, bg=UI.BG_SEC)
        f.pack(side=tk.LEFT, padx=20)
        tk.Label(f, text=title, bg=UI.BG_SEC, fg="#71717a", font=('Segoe UI', 7, 'bold')).pack(anchor="e")
        tk.Label(f, textvariable=var, bg=UI.BG_SEC, fg=color, font=('Segoe UI', 14, 'bold')).pack(anchor="e")

    def setup_bulk_tab(self):
        sidebar = tk.Frame(self.tab_bulk, bg=UI.BG, width=300)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 25), pady=25)

        self.render_config(sidebar)
        
        filter_frame = UI.label_frame(sidebar, "FILTERS")
        filter_frame.pack(fill=tk.X, pady=15)
        UI.checkbox(filter_frame, "Hide Taken Results", self.hide_taken).pack(anchor="w", padx=15, pady=8)
        UI.checkbox(filter_frame, "Use Proxies (proxies.txt)", tk.BooleanVar(value=settings.get("use_proxies"))).pack(anchor="w", padx=15, pady=8)

        UI.button(sidebar, "GENERATE LIST", self.generate_usernames).pack(fill=tk.X, pady=6)
        self.btn_start = UI.button(sidebar, "START CHECKING", self.start_bulk, primary=True)
        self.btn_start.pack(fill=tk.X, pady=6)
        UI.button(sidebar, "EXPORT RESULTS", self.export_results).pack(fill=tk.X, pady=6)
        UI.button(sidebar, "STOP PROCESS", self.stop_audit).pack(fill=tk.X, pady=6)

        self.console = UI.console(self.tab_bulk)
        self.console.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=25)

    def setup_monitor_tab(self):
        f = tk.Frame(self.tab_monitor, bg=UI.BG)
        f.pack(fill=tk.BOTH, expand=True, padx=60, pady=60)
        
        tk.Label(f, text="TARGET USERNAME", bg=UI.BG, fg=UI.FG_SEC, font=('Segoe UI', 9, 'bold')).pack(anchor="w")
        self.monitor_target = UI.entry(f)
        self.monitor_target.pack(fill=tk.X, pady=(8, 25))
        
        tk.Label(f, text="CHECK INTERVAL (SECONDS)", bg=UI.BG, fg=UI.FG_SEC, font=('Segoe UI', 9, 'bold')).pack(anchor="w")
        self.monitor_delay = UI.entry(f)
        self.monitor_delay.insert(0, "60")
        self.monitor_delay.pack(fill=tk.X, pady=(8, 25))
        
        self.btn_monitor = UI.button(f, "ACTIVATE SNIPER", self.start_monitor, primary=True)
        self.btn_monitor.pack(fill=tk.X)
        
        self.monitor_log = UI.console(f)
        self.monitor_log.pack(fill=tk.BOTH, expand=True, pady=30)

    def render_config(self, parent):
        frame = UI.label_frame(parent, "PLATFORMS")
        frame.pack(fill=tk.X, pady=15)
        
        self.vars = {
            "pinterest": tk.BooleanVar(value=settings.get("platforms.pinterest")),
            "instagram": tk.BooleanVar(value=settings.get("platforms.instagram")),
            "github": tk.BooleanVar(value=settings.get("platforms.github"))
        }
        for k, v in self.vars.items():
            UI.checkbox(frame, k.title(), v).pack(anchor="w", padx=15, pady=4)

        tk.Label(frame, text="Count / Length", bg=UI.BG, fg=UI.FG_SEC, font=('Segoe UI', 8)).pack(anchor="w", padx=15, pady=(15, 5))
        self.ent_count = UI.entry(frame)
        self.ent_count.pack(fill=tk.X, padx=15)
        self.ent_count.insert(0, "100")
        self.ent_length = UI.entry(frame)
        self.ent_length.pack(fill=tk.X, padx=15, pady=8)
        self.ent_length.insert(0, "4")

    def log(self, message, tag="info", console=None):
        target = console or self.console
        target.config(state="normal")
        target.insert("end", f"{message}\n", tag)
        target.see("end")
        target.config(state="disabled")

    def generate_usernames(self):
        try:
            count = int(self.ent_count.get())
            length = int(self.ent_length.get())
            self.targets = []
            chars = string.ascii_lowercase + string.digits
            for _ in range(count):
                self.targets.append("".join(random.choices(chars, k=length)))
            self.log(f"[*] Generated {len(self.targets)} targets.", "info")
        except: pass

    def save_config(self):
        settings.set("platforms.pinterest", self.vars["pinterest"].get())
        settings.set("platforms.instagram", self.vars["instagram"].get())
        settings.set("platforms.github", self.vars["github"].get())
        settings.save()

    def start_bulk(self):
        if not self.targets: return
        self.save_config()
        self.reset_stats()
        
        self.btn_start.config(state="disabled")
        self.status.config(text="BULK CHECK RUNNING...")
        
        thread = threading.Thread(target=self.run_bulk_engine)
        thread.daemon = True
        thread.start()

    def run_bulk_engine(self):
        self.engine.start_bulk(self.targets, self.handle_result)
        self.root.after(0, self.finish_audit)

    def start_monitor(self):
        target = self.monitor_target.get()
        if not target: return
        self.save_config()
        
        self.btn_monitor.config(state="disabled", text="MONITORING...")
        self.status.config(text=f"SNIPER ACTIVE: {target}")
        
        try: delay = int(self.monitor_delay.get())
        except: delay = 60
        
        thread = threading.Thread(target=lambda: self.engine.start_monitor(target, self.handle_monitor_result, delay))
        thread.daemon = True
        thread.start()

    def handle_result(self, data):
        self.stat_total.set(self.stat_total.get() + 1)
        username = data["username"]
        timestamp = data["timestamp"]
        
        if data["available_on"]:
            self.stat_avail.set(self.stat_avail.get() + 1)
            self.results_cache.append(data)
            platforms = ", ".join([p.upper() for p in data["available_on"]])
            msg = f"[{timestamp}] [+] {username:<15} | AVAILABLE: {platforms}"
            self.root.after(0, lambda: self.log(msg, "success"))
        else:
            if not self.hide_taken.get():
                msg = f"[{timestamp}] [-] {username:<15} | TAKEN"
                self.root.after(0, lambda: self.log(msg, "fail"))

    def handle_monitor_result(self, data):
        timestamp = data["timestamp"]
        if data["available_on"]:
            msg = f"[{timestamp}] 💎 AVAILABLE ON: {', '.join(data['available_on'])}"
            self.root.after(0, lambda: self.log(msg, "success", self.monitor_log))
        else:
            msg = f"[{timestamp}] Still taken..."
            self.root.after(0, lambda: self.log(msg, "fail", self.monitor_log))

    def reset_stats(self):
        self.stat_total.set(0)
        self.stat_avail.set(0)
        self.results_cache = []
        self.console.config(state="normal")
        self.console.delete(1.0, "end")
        self.console.config(state="disabled")

    def finish_audit(self):
        self.btn_start.config(state="normal")
        self.status.config(text="READY")
        self.log("[*] Bulk check completed.", "info")

    def stop_audit(self):
        self.engine.stop()
        self.btn_monitor.config(state="normal", text="ACTIVATE SNIPER")
        self.log("[!] Stopping engine...", "info")
        
    def export_results(self):
        if not self.results_cache: return
        f = filedialog.asksaveasfilename(defaultextension=".txt")
        if f:
            with open(f, "w") as file:
                for item in self.results_cache:
                    file.write(f"{item['username']} : {', '.join(item['available_on'])}\n")
            messagebox.showinfo("Export", f"Saved {len(self.results_cache)} usernames.")

    def run(self):
        self.root.mainloop()
