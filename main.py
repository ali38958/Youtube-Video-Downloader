import tkinter as tk
import ttkbootstrap as tb
from PIL import Image, ImageTk
import os
from ui.theme import theme_mgr
from ui.main_window import MainWindow

def main():
    initial_tb_theme = theme_mgr.current_theme.get("tb_theme", "darkly")
    root = tb.Window(themename=initial_tb_theme)
    root.title("YT // RAW LOADER — Neo-Brutalist Video Downloader")
    root.geometry("1150x780")
    root.minsize(880, 620)
    
    # Set Window & Taskbar Icon
    ico_path = os.path.join(os.path.dirname(__file__), "assets", "logo.ico")
    png_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
    
    if os.path.exists(ico_path):
        try:
            root.iconbitmap(ico_path)
        except Exception:
            pass
            
    if os.path.exists(png_path):
        try:
            app_icon = ImageTk.PhotoImage(Image.open(png_path).resize((64, 64), Image.Resampling.LANCZOS))
            root.iconphoto(False, app_icon)
        except Exception:
            pass
    
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
