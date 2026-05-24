import tkinter as tk

class ModernButton(tk.Button):
    def __init__(self, master, text="", color="#3498db", variant="active", font_size=12, command=None, width=10, height=1):
        self.color = color
        self.variant = variant
        self.active = variant == "active"
        
        super().__init__(
            master, text=text, font=("Arial", font_size, "bold"),
            bg=color, fg="white", relief=tk.FLAT, borderwidth=0,
            activebackground=self._darken_color(color, 0.8) if self.active else color,
            activeforeground="white", cursor="hand2" if self.active else "arrow",
            width=width, height=height, command=command if self.active else None
        )
        
        self.config(highlightthickness=0, bd=0)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _darken_color(self, color, factor=0.7):
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _on_enter(self, event):
        if self.active:
            self.config(bg=self._darken_color(self.color, 0.85))
    
    def _on_leave(self, event):
        if self.active:
            self.config(bg=self.color)