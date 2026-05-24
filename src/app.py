import tkinter as tk
import os
import sys
import requests
import re
from pytube import YouTube
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


    def open_settings(self):
        pass

    def handle_search(self, url):
        try:
            requests.get("https://www.youtube.com", timeout=5)
        except:
            print("No internet")
            return
        
        if not re.match(r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$', url):
            print("Invalid YouTube URL")
            return
        
        try:
            import yt_dlp
            
            ydl_opts = {
                "quiet": True,
                "cookiefile": "cookies.txt",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "extractor_args": {"youtube": {"player_client": ["tv_embedded"]}},
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
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
                
                print(f"Video: {info.get('title')}")
                
        except Exception as e:
            print(f"Error: {e}")

def main():
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()