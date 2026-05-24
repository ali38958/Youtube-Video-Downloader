import tkinter as tk
import os
import sys
import requests
import re
import yt_dlp
import urllib.request
import json
from io import BytesIO
from tkinter import filedialog
from datetime import datetime
import threading
import subprocess
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PIL import Image, ImageTk
from components.button import ModernButton
from components.input_field import SearchInput
from components.dropdown import ModernDropdown

class YouTubeDownloaderApp(tk.Frame):
    def __init__(self, master=None, assets_dir=None):
        super().__init__(master)
        self.assets_dir = assets_dir
        self.master = master
        self.master.title("YouTube Video Downloader")
        self.master.geometry("800x700")
        self.master.resizable(False, False)
        
        self.app_data_dir = "C://ytdownlod"
        os.makedirs(self.app_data_dir, exist_ok=True)
        
        # Default download location
        self.download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        self.history_file = os.path.join(self.app_data_dir, "download_history.json")
        self.settings_file = os.path.join(self.app_data_dir, "settings.json")
        
        self.active_downloads = {}  # id -> {thread, process, title, status, pause_event, stop_flag}
        self.download_counter = 0
        
        self.load_settings()
        self.load_history()
        
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
        
        # Download manager button
        download_btn = ModernButton(content, text="📥", color="#3b82f6", variant="active", font_size=14, command=self.open_download_manager, width=3, height=1)
        download_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Settings button
        setting_btn = ModernButton(content, text="⚙️", color="#34495e", variant="active", font_size=14, command=self.open_settings, width=3, height=1)
        setting_btn.pack(side=tk.RIGHT)

        # Main content area
        main_frame = tk.Frame(self.master, bg="#f5f5f5")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Search input component
        from components.input_field import SearchInput
        self.search_input = SearchInput(main_frame, label_text="Video URL", button_text="Search", button_color="#3498db", on_search=self.handle_search)
        self.search_input.pack(fill=tk.X, pady=(0, 20))

        # Dropdowns container
        dropdowns_frame = tk.Frame(main_frame, bg="#f5f5f5")
        dropdowns_frame.pack(fill=tk.X, pady=(0, 20))
        
        from components.dropdown import ModernDropdown
        
        # Format dropdown
        self.format_dropdown = ModernDropdown(
            dropdowns_frame, 
            label_text="Format", 
            options=["N/A"], 
            default="N/A",
            disabled=True
        )
        self.format_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Quality dropdown
        self.quality_dropdown = ModernDropdown(
            dropdowns_frame, 
            label_text="Quality", 
            options=["N/A"], 
            default="N/A",
            disabled=True
        )
        self.quality_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Thumbnail and trim section
        trim_frame = tk.Frame(main_frame, bg="#f5f5f5")
        trim_frame.pack(fill=tk.BOTH, pady=(0, 20))

        # Thumbnail
        self.thumbnail_label = tk.Label(trim_frame, bg="#f5f5f5")
        self.thumbnail_label.pack(pady=(0, 10))

        # Time range frame
        time_frame = tk.Frame(trim_frame, bg="#f5f5f5")
        time_frame.pack(fill=tk.X)

        # From time
        from_frame = tk.Frame(time_frame, bg="#f5f5f5")
        from_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        tk.Label(from_frame, text="From:", font=("Inter", 10), bg="#f5f5f5").pack(anchor="w")
        self.from_scale = tk.Scale(from_frame, from_=0, to=0, orient=tk.HORIZONTAL, bg="#f5f5f5", highlightthickness=0)
        self.from_scale.pack(fill=tk.X)
        self.from_label = tk.Label(from_frame, text="00:00:00", font=("Inter", 9), bg="#f5f5f5")
        self.from_label.pack()

        # To time
        to_frame = tk.Frame(time_frame, bg="#f5f5f5")
        to_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Label(to_frame, text="To:", font=("Inter", 10), bg="#f5f5f5").pack(anchor="w")
        self.to_scale = tk.Scale(to_frame, from_=0, to=0, orient=tk.HORIZONTAL, bg="#f5f5f5", highlightthickness=0)
        self.to_scale.pack(fill=tk.X)
        self.to_label = tk.Label(to_frame, text="00:00:00", font=("Inter", 9), bg="#f5f5f5")
        self.to_label.pack()

        # Download button
        self.download_btn = ModernButton(main_frame, text="Download", color="#22c55e", variant="active", font_size=14, command=self.start_download, width=15, height=1)
        self.download_btn.pack(pady=20)

        self.current_video_info = None

    def _sec_to_time(self, seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def _update_labels(self, *args):
        from_sec = self.from_scale.get()
        to_sec = self.to_scale.get()
        if from_sec >= to_sec:
            self.from_scale.set(to_sec - 1)
            from_sec = to_sec - 1
        self.from_label.config(text=self._sec_to_time(from_sec))
        self.to_label.config(text=self._sec_to_time(to_sec))

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                self.download_dir = settings.get("download_dir", self.download_dir)
    
    def save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump({"download_dir": self.download_dir}, f)
    
    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                self.history = json.load(f)
        else:
            self.history = []
    
    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history[-100:], f)  # Keep last 100
    
    def add_to_history(self, title, format_val, quality, file_path):
        self.history.append({
            "title": title,
            "format": format_val,
            "quality": quality,
            "file_path": file_path,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self.save_history()
    
    def open_settings(self):
        settings_win = tk.Toplevel(self.master)
        settings_win.title("Settings")
        settings_win.geometry("400x200")
        settings_win.resizable(False, False)
        
        tk.Label(settings_win, text="Default Download Location:", font=("Arial", 10)).pack(pady=(20, 5))
        dir_var = tk.StringVar(value=self.download_dir)
        entry = tk.Entry(settings_win, textvariable=dir_var, width=40)
        entry.pack(pady=5)
        
        def browse():
            selected = filedialog.askdirectory()
            if selected:
                dir_var.set(selected)
        
        tk.Button(settings_win, text="Browse", command=browse).pack(pady=5)
        
        def save():
            self.download_dir = dir_var.get()
            os.makedirs(self.download_dir, exist_ok=True)
            self.save_settings()
            settings_win.destroy()
        
        tk.Button(settings_win, text="Save", command=save, bg="#22c55e", fg="white").pack(pady=20)
    
    def open_download_manager(self):
        win = tk.Toplevel(self.master)
        win.title("Download Manager")
        win.geometry("600x500")
        win.resizable(False, False)
        
        notebook = tk.Frame(win)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Active downloads tab
        active_frame = tk.Frame(notebook)
        active_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(active_frame, text="Active Downloads", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        active_canvas = tk.Canvas(active_frame, highlightthickness=0)
        scrollbar = tk.Scrollbar(active_frame, orient="vertical", command=active_canvas.yview)
        active_scroll = tk.Frame(active_canvas)
        active_canvas.create_window((0, 0), window=active_scroll, anchor="nw")
        active_canvas.configure(yscrollcommand=scrollbar.set)
        active_scroll.bind("<Configure>", lambda e: active_canvas.configure(scrollregion=active_canvas.bbox("all")))
        active_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # History tab
        history_frame = tk.Frame(notebook)
        history_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(history_frame, text="Download History", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        history_canvas = tk.Canvas(history_frame, highlightthickness=0)
        history_scrollbar = tk.Scrollbar(history_frame, orient="vertical", command=history_canvas.yview)
        history_scroll = tk.Frame(history_canvas)
        history_canvas.create_window((0, 0), window=history_scroll, anchor="nw")
        history_canvas.configure(yscrollcommand=history_scrollbar.set)
        history_scroll.bind("<Configure>", lambda e: history_canvas.configure(scrollregion=history_canvas.bbox("all")))
        history_canvas.pack(side="left", fill="both", expand=True)
        history_scrollbar.pack(side="right", fill="y")
        
        # Populate active downloads
        def refresh_active():
            for widget in active_scroll.winfo_children():
                widget.destroy()
            for download_id, data in self.active_downloads.items():
                frame = tk.Frame(active_scroll, relief=tk.SOLID, bd=1)
                frame.pack(fill=tk.X, pady=5)
                tk.Label(frame, text=data['title'], font=("Arial", 10)).pack(anchor="w", padx=5, pady=(5, 0))
                progress = ttk.Progressbar(frame, mode='determinate')
                progress.pack(fill=tk.X, padx=5, pady=5)
                data['progress_bar'] = progress
                status_label = tk.Label(frame, text="Downloading...", font=("Arial", 8))
                status_label.pack(anchor="w", padx=5)
                btn_frame = tk.Frame(frame)
                btn_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
                pause_btn = tk.Button(btn_frame, text="⏸", command=lambda: self.pause_download(download_id, pause_btn))
                pause_btn.pack(side=tk.RIGHT, padx=2)
                stop_btn = tk.Button(btn_frame, text="✖", fg="red", command=lambda: self.stop_download(download_id))
                stop_btn.pack(side=tk.RIGHT, padx=2)
                data['pause_btn'] = pause_btn
                data['stop_btn'] = stop_btn
                data['status_label'] = status_label
            if not self.active_downloads:
                tk.Label(active_scroll, text="No active downloads", fg="gray").pack(pady=20)
        
        # Populate history
        def refresh_history():
            for widget in history_scroll.winfo_children():
                widget.destroy()
            for item in reversed(self.history[-20:]):
                frame = tk.Frame(history_scroll, relief=tk.SOLID, bd=1)
                frame.pack(fill=tk.X, pady=5)
                tk.Label(frame, text=item['title'], font=("Arial", 10, "bold")).pack(anchor="w", padx=5, pady=(5, 0))
                tk.Label(frame, text=f"Format: {item['format']} | Quality: {item['quality']} | Date: {item['date']}", font=("Arial", 8)).pack(anchor="w", padx=5)
                tk.Label(frame, text=f"Saved to: {item['file_path']}", font=("Arial", 8), fg="gray").pack(anchor="w", padx=5, pady=(0, 5))
                btn = tk.Button(frame, text="📁 Open Folder", command=lambda p=item['file_path']: os.startfile(os.path.dirname(p)))
                btn.pack(anchor="e", padx=5, pady=(0, 5))
        
        refresh_active()
        refresh_history()
        
        # Refresh every 1 second for active downloads
        def periodic_refresh():
            refresh_active()
            win.after(1000, periodic_refresh)
        periodic_refresh()
    
    def pause_download(self, download_id, pause_btn):
        data = self.active_downloads.get(download_id)
        if data:
            data['paused'] = not data.get('paused', False)
            pause_btn.config(text="▶" if data['paused'] else "⏸")
            if not data['paused']:
                data['status_label'].config(text="Resuming...")
    
    def stop_download(self, download_id):
        data = self.active_downloads.get(download_id)
        if data:
            data['stop_flag'] = True
            data['status_label'].config(text="Stopping...")
    
    def handle_search(self, url):
        try:
            requests.get("https://8.8.8.8", timeout=3)
        except:
            print("No internet")
            return
        
        if not re.match(r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$', url):
            print("Invalid YouTube URL")
            return
        
        try:
            ydl_opts = {
                "quiet": True,
                "cookiefile": "cookies.txt",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "extractor_args": {"youtube": {"player_client": ["tv_embedded"]}},
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                self.current_video_info = info
                
                formats = []
                qualities = []
                
                for f in info.get("formats", []):
                    if f.get("vcodec") != "none" and f.get("height"):
                        ext = f.get("ext", "unknown")
                        if ext not in formats:
                            formats.append(ext)
                        quality = f"{f.get('height')}p"
                        if quality not in qualities:
                            qualities.append(quality)
                
                formats = list(dict.fromkeys(formats))
                qualities = list(dict.fromkeys(qualities))
                qualities.sort(key=lambda x: int(x.replace('p', '')) if x != 'N/A' else 0, reverse=True)
                
                self.format_dropdown.set_options(formats if formats else ["N/A"])
                self.quality_dropdown.set_options(qualities if qualities else ["N/A"])
                self.format_dropdown.set_disabled(False)
                self.quality_dropdown.set_disabled(False)
                
                # Load thumbnail
                thumbnail_url = info.get("thumbnail")
                if thumbnail_url:
                    try:
                        req = urllib.request.urlopen(thumbnail_url)
                        img_data = req.read()
                        img = Image.open(BytesIO(img_data))
                        img = img.resize((160, 90), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        self.thumbnail_label.config(image=photo)
                        self.thumbnail_label.image = photo
                    except:
                        pass
                
                # Set duration and scale ranges
                duration = info.get("duration", 0)
                self.from_scale.config(to=duration)
                self.to_scale.config(to=duration)
                self.to_scale.set(duration)
                self.from_scale.set(0)
                
                self.from_scale.config(command=self._update_labels)
                self.to_scale.config(command=self._update_labels)
                self._update_labels()
                
                print(f"Video: {info.get('title')}")
                
        except Exception as e:
            print(f"Error: {e}")
    
    def start_download(self):
        if not self.current_video_info:
            print("No video loaded")
            return
        
        format_val = self.format_dropdown.get()
        quality_val = self.quality_dropdown.get()
        from_sec = self.from_scale.get()
        to_sec = self.to_scale.get()
        
        download_id = self.download_counter
        self.download_counter += 1
        
        pause_event = threading.Event()
        stop_flag = threading.Event()
        
        self.active_downloads[download_id] = {
            'title': self.current_video_info.get('title', 'Video'),
            'pause_event': pause_event,
            'stop_flag': stop_flag,
            'paused': False
        }
        
        def download_task():
            import time
            output_template = os.path.join(self.download_dir, "%(title)s.%(ext)s")
            final_file = None
            
            def progress_hook(d):
                if stop_flag.is_set():
                    raise Exception("Download stopped")
                while pause_event.is_set():
                    time.sleep(0.5)
                    if stop_flag.is_set():
                        raise Exception("Download stopped")
                if d['status'] == 'downloading':
                    percent = d.get('_percent_str', '0%').replace('%', '').strip()
                    try:
                        p = float(percent)
                        if download_id in self.active_downloads and 'progress_bar' in self.active_downloads[download_id]:
                            self.master.after(0, lambda: self.active_downloads[download_id]['progress_bar'].config(value=p))
                            self.master.after(0, lambda: self.active_downloads[download_id]['status_label'].config(text=f"Downloading: {percent}%"))
                    except:
                        pass
                elif d['status'] == 'finished':
                    nonlocal final_file
                    final_file = d.get('filename')
            
            try:
                ydl_opts = {
                    "outtmpl": output_template,
                    "format": f"bestvideo[height<={quality_val.replace('p','')}][ext={format_val}]+bestaudio[ext={format_val}]/best[ext={format_val}]",
                    "merge_output_format": format_val,
                    "quiet": True,
                    "progress_hooks": [progress_hook],
                    "cookiefile": "cookies.txt",
                }
                if from_sec > 0 or to_sec:
                    ydl_opts["download_ranges"] = lambda info, _: [{"start_time": from_sec, "end_time": to_sec}]
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([self.current_video_info["webpage_url"]])
                
                if final_file and os.path.exists(final_file):
                    self.add_to_history(self.current_video_info.get('title', 'Video'), format_val, quality_val, final_file)
                
                self.master.after(0, lambda: self.active_downloads[download_id]['status_label'].config(text="Completed!"))
                self.master.after(0, lambda: self.active_downloads[download_id]['pause_btn'].config(state="disabled"))
                self.master.after(0, lambda: self.active_downloads[download_id]['stop_btn'].config(state="disabled"))
                
            except Exception as e:
                if not stop_flag.is_set():
                    self.master.after(0, lambda: self.active_downloads[download_id]['status_label'].config(text=f"Failed: {str(e)[:50]}"))
            finally:
                self.master.after(3000, lambda: self.active_downloads.pop(download_id, None))
        
        thread = threading.Thread(target=download_task, daemon=True)
        self.active_downloads[download_id]['thread'] = thread
        thread.start()
        
        self.open_download_manager()

def main():
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()