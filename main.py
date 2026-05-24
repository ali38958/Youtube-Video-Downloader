import os
import sys
import tkinter as tk

base_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(base_dir, "assets")
sys.path.append(base_dir)

from src.app import YouTubeDownloaderApp

def main():
    root = tk.Tk()
    app = YouTubeDownloaderApp(root, assets_dir=assets_dir)
    root.mainloop()

if __name__ == "__main__":
    main()