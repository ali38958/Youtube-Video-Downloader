import tkinter as tk

class SearchInput(tk.Frame):
    def __init__(self, master, label_text="Video URL", button_text="Search", button_color="#2563eb", on_search=None):
        super().__init__(master, bg=master.cget("bg"))
        
        self.on_search = on_search
        
        # Label
        self.label = tk.Label(self, text=label_text, font=("Inter", 12, "bold"), fg="#374151", anchor="w")
        self.label.pack(fill=tk.X, pady=(0, 8))
        
        # Container for input + button
        self.input_frame = tk.Frame(self, bg="white")
        self.input_frame.pack(fill=tk.X)
        
        # Entry with custom styling
        self.entry = tk.Entry(
            self.input_frame, 
            font=("Inter", 12), 
            relief=tk.FLAT, 
            bd=0,
            highlightthickness=1,
            highlightcolor="#2563eb",
            highlightbackground="#d1d5db",
            fg="#1f2937",
            bg="white"
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=12, padx=(0, 10))
        
        # Placeholder
        self.placeholder = "https://www.youtube.com/watch?v=..."
        self._set_placeholder()
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        
        # Search button with modern style
        self.button = tk.Button(
            self.input_frame, text=button_text, bg=button_color, fg="white",
            font=("Inter", 11, "bold"), relief=tk.FLAT, bd=0,
            padx=24, pady=10, cursor="hand2",
            activebackground="#1d4ed8", activeforeground="white",
            command=self._on_search
        )
        self.button.pack(side=tk.RIGHT)
        
        # Add shadow effect for container
        self.input_frame.config(highlightthickness=1, highlightbackground="#e5e7eb", highlightcolor="#e5e7eb")
    
    def _set_placeholder(self):
        self.entry.insert(0, self.placeholder)
        self.entry.config(fg="#9ca3af")
    
    def _on_focus_in(self, event):
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg="#1f2937")
    
    def _on_focus_out(self, event):
        if not self.entry.get():
            self._set_placeholder()
    
    def _on_search(self):
        url = self.entry.get()
        if url and url != self.placeholder and self.on_search:
            self.on_search(url)
    
    def get(self):
        val = self.entry.get()
        return val if val != self.placeholder else ""
    
    def clear(self):
        self.entry.delete(0, tk.END)
        self._set_placeholder()