import os
import sys
import tkinter as tk

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.app import YouTubeDownloaderApp


def main():
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
