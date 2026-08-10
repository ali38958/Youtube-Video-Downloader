import tkinter as tk
import ttkbootstrap as tb
from ui.main_window import MainWindow

def main():
    root = tb.Window(themename="darkly")
    root.title("YouTube Video Downloader")
    root.geometry("1100x750")
    root.minsize(800, 600)
    
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
