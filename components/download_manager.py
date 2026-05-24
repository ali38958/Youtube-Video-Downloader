import tkinter as tk
from tkinter import ttk
import os
import json
import threading

class DownloadManager(tk.Toplevel):
    def __init__(self, master, download_dir):
        super().__init__(master)
        self.title("Download Manager")
        self.geometry("500x400")
        self.resizable(False, False)
        self.download_dir = download_dir
        self.downloads = []  # list of dicts: {id, title, status, progress, thread, process}
        self.next_id = 1
        
        # Main frame
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        tk.Label(main_frame, text="Active Downloads", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        
        # Canvas + Scrollbar
        canvas_frame = tk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.downloads_container = self.scrollable_frame
    
    def add_download(self, title, download_func, *args):
        download_id = self.next_id
        self.next_id += 1
        
        frame = tk.Frame(self.downloads_container, relief=tk.SOLID, bd=1)
        frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Title
        tk.Label(frame, text=title, font=("Arial", 10), anchor="w").pack(fill=tk.X, padx=5, pady=(5, 0))
        
        # Progress bar
        progress = ttk.Progressbar(frame, mode='determinate')
        progress.pack(fill=tk.X, padx=5, pady=5)
        
        # Status label and buttons frame
        bottom_frame = tk.Frame(frame)
        bottom_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        status_label = tk.Label(bottom_frame, text="Starting...", font=("Arial", 8), anchor="w")
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Buttons
        pause_btn = tk.Button(bottom_frame, text="⏸", width=2, command=lambda: self.pause_download(download_id))
        pause_btn.pack(side=tk.RIGHT, padx=2)
        
        stop_btn = tk.Button(bottom_frame, text="✖", width=2, fg="red", command=lambda: self.stop_download(download_id))
        stop_btn.pack(side=tk.RIGHT, padx=2)
        
        download_info = {
            "id": download_id,
            "title": title,
            "frame": frame,
            "progress": progress,
            "status_label": status_label,
            "pause_btn": pause_btn,
            "stop_btn": stop_btn,
            "paused": False,
            "stopped": False,
            "thread": None,
            "process": None
        }
        
        self.downloads.append(download_info)
        
        # Start download in thread
        thread = threading.Thread(target=self._run_download, args=(download_id, download_func, args))
        thread.daemon = True
        download_info["thread"] = thread
        thread.start()
        
        return download_id
    
    def _run_download(self, download_id, download_func, args):
        import time
        download_info = next(d for d in self.downloads if d["id"] == download_id)
        
        def progress_hook(d):
            if download_info["stopped"]:
                raise Exception("Download stopped")
            while download_info["paused"]:
                time.sleep(0.5)
                if download_info["stopped"]:
                    raise Exception("Download stopped")
            if d['status'] == 'downloading':
                percent = d.get('_percent_str', '0%').replace('%', '').strip()
                try:
                    p = float(percent)
                    download_info["progress"]['value'] = p
                    download_info["status_label"].config(text=f"Downloading: {percent}%")
                except:
                    pass
            elif d['status'] == 'finished':
                download_info["progress"]['value'] = 100
                download_info["status_label"].config(text="Completed!")
                download_info["pause_btn"].config(state="disabled")
                download_info["stop_btn"].config(text="✓", fg="green", state="disabled")
        
        try:
            download_func(progress_hook=progress_hook, *args)
        except Exception as e:
            if not download_info["stopped"]:
                download_info["status_label"].config(text=f"Failed: {str(e)[:50]}")
    
    def pause_download(self, download_id):
        download_info = next(d for d in self.downloads if d["id"] == download_id)
        download_info["paused"] = not download_info["paused"]
        download_info["pause_btn"].config(text="▶" if download_info["paused"] else "⏸")
        if not download_info["paused"]:
            download_info["status_label"].config(text="Resuming...")
    
    def stop_download(self, download_id):
        download_info = next(d for d in self.downloads if d["id"] == download_id)
        download_info["stopped"] = True
        download_info["status_label"].config(text="Stopped")
        download_info["pause_btn"].config(state="disabled")
        download_info["stop_btn"].config(text="✖", state="disabled")