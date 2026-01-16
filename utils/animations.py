import tkinter as tk
from typing import Callable, Optional


class AnimationEngine:
    @staticmethod
    def fade_in(widget: tk.Widget, duration: int = 200, callback: Optional[Callable] = None):
        if callback:
            widget.after(duration, callback)
    
    @staticmethod
    def slide_in(widget: tk.Widget, from_x: int, to_x: int, duration: int = 300):
        steps = 20
        step_size = (to_x - from_x) / steps
        delay = duration // steps
        
        def animate(step: int):
            if step < steps:
                new_x = from_x + (step_size * step)
                widget.place(x=new_x)
                widget.after(delay, lambda: animate(step + 1))
        
        animate(0)
    
    @staticmethod
    def count_up(variable: tk.IntVar, target: int, duration: int = 500):
        current = variable.get()
        if current == target:
            return
        
        steps = min(30, abs(target - current))
        step_size = (target - current) / steps
        delay = duration // steps
        
        def animate(step: int):
            if step < steps:
                new_val = int(current + (step_size * (step + 1)))
                variable.set(new_val)
                variable._root().after(delay, lambda: animate(step + 1))
            else:
                variable.set(target)
        
        animate(0)
    
    @staticmethod
    def pulse(widget: tk.Widget, count: int = 3):
        try:
            original_bg = widget.cget('bg')
            
            def animate(pulse: int, growing: bool = True):
                if pulse >= count:
                    widget.config(bg=original_bg)
                    return
                
                if growing:
                    widget.after(100, lambda: animate(pulse, False))
                else:
                    widget.config(bg=original_bg)
                    widget.after(100, lambda: animate(pulse + 1, True))
            
            animate(0)
        except Exception:
            pass
