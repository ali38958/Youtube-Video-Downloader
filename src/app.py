import tkinter as tk

class YouTubeDownloaderApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Youtube Video Downloader")
        self.master.geometry("800x700")
        self.master.resizable(False, False)


def main():
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()