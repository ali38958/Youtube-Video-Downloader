import tkinter as tk
from tkinter import ttk

class ModernDropdown(tk.Frame):
    def __init__(self, master, label_text="", options=["N/A"], default="N/A", disabled=True):
        super().__init__(master, bg=master.cget("bg"))
        
        # Label
        self.label = tk.Label(self, text=label_text, font=("Inter", 11, "bold"), fg="#374151", anchor="w")
        self.label.pack(fill=tk.X, pady=(0, 5))
        
        # Combobox
        self.combo = ttk.Combobox(self, values=options, font=("Inter", 11), state="disabled" if disabled else "readonly")
        self.combo.pack(fill=tk.X, ipady=8)
        
        if default and default in options:
            self.combo.set(default)
        elif options:
            self.combo.set(options[0])
    
    def set_disabled(self, disabled=True):
        self.combo.config(state="disabled" if disabled else "readonly")
    
    def get(self):
        return self.combo.get()
    
    def set_options(self, options):
        self.combo.config(values=options)
        if options:
            self.combo.set(options[0])