import tkinter as tk
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PIL import Image, ImageTk
from components.button import ModernButton

class YouTubeDownloaderApp(tk.Frame):
    def __init__(self, master=None, assets_dir=None):
        super().__init__(master)
        self.assets_dir = assets_dir
        self.master = master
        self.master.title("YouTube Video Downloader")
        self.master.geometry("800x700")
        self.master.resizable(False, False)
        
        # Header panel
        header_panel = tk.Frame(self.master, bg="white")
        header_panel.pack(fill=tk.X)
        
        # Bottom border
        tk.Frame(header_panel, height=2, bg="#cccccc").pack(side=tk.BOTTOM, fill=tk.X)
        
        # Content inside header
        content = tk.Frame(header_panel, bg="white")
        content.pack(fill=tk.X, padx=20, pady=15)
        
        # Logo
        if self.assets_dir:
            img_path = os.path.join(self.assets_dir, "logo.png")
            if os.path.exists(img_path):
                img = Image.open(img_path)
                img = img.resize((40, 40), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                img_label = tk.Label(content, image=photo, bg="white")
                img_label.image = photo
                img_label.pack(side=tk.LEFT, padx=(0, 8))
        
        # Title
        title_label = tk.Label(content, text="YouTube Video Downloader", font=("Arial", 14, "bold"), bg="white")
        title_label.pack(side=tk.LEFT)
        
        # Settings button
        setting_btn = ModernButton(content, text="⚙️", color="#34495e", variant="active", font_size=14, command=self.open_settings, width=3, height=1)
        setting_btn.pack(side=tk.RIGHT)

    def open_settings(self):
        pass

def main():
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()