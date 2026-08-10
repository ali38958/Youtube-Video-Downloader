import yt_dlp
import threading
import os
import glob

class DownloadTask:
    def __init__(self, url, quality, title):
        self.url = url
        self.quality = quality
        self.title = title
        self.is_cancelled = False
        self.pause_event = threading.Event()
        self.pause_event.set() # True = running, False = paused
        self.thread = None
        self.status = "Queued" # Downloading, Paused, Cancelled, Completed, Failed
        self.progress_str = "0%"
        self.speed_str = "N/A"

    def pause(self):
        self.status = "Paused"
        self.pause_event.clear()
        
    def resume(self):
        self.status = "Downloading"
        self.pause_event.set()
        
    def cancel(self):
        self.is_cancelled = True
        self.status = "Cancelled"
        self.pause_event.set()

class Downloader:
    def __init__(self, download_folder, progress_callback=None, finished_callback=None, error_callback=None):
        self.download_folder = download_folder
        self.progress_callback = progress_callback
        self.finished_callback = finished_callback
        self.error_callback = error_callback
        
        self.tasks = {} 

    def fetch_formats(self, url):
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                
                available_formats = set()
                for f in formats:
                    if f.get('vcodec') != 'none':
                        h = f.get('height')
                        if h:
                            available_formats.add(h)
                
                format_list = sorted(list(available_formats), reverse=True)
                str_formats = [f"{h}p" for h in format_list]
                str_formats.append("Audio Only")
                
                if not str_formats:
                    return ["1080p", "720p", "480p", "360p", "Audio Only"]
                return str_formats
        except Exception:
            return ["1080p", "720p", "480p", "360p", "Audio Only"]

    def _progress_hook(self, d, task):
        if task.is_cancelled:
            raise Exception("Download cancelled by user")
            
        if not task.pause_event.is_set():
            task.pause_event.wait()
            if task.is_cancelled:
                raise Exception("Download cancelled by user")

        if d['status'] == 'downloading':
            if self.progress_callback:
                percent_str = d.get('_percent_str', '0%').strip('\x1b[0;39m').strip()
                speed_str = d.get('_speed_str', 'N/A').strip('\x1b[0;39m').strip()
                task.progress_str = percent_str
                task.speed_str = speed_str
                self.progress_callback(task.url, percent_str, speed_str)
                
        elif d['status'] == 'finished':
            if self.progress_callback:
                task.progress_str = "100%"
                task.speed_str = "Processing..."
                self.progress_callback(task.url, "100%", "Processing...")

    def _download_task_runner(self, task):
        ydl_opts = {
            'outtmpl': f'{self.download_folder}/%(title)s.%(ext)s',
            'progress_hooks': [lambda d: self._progress_hook(d, task)],
            'quiet': True,
            'no_warnings': True,
            'continuedl': True,
        }
        
        if task.quality == 'Audio Only':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            h = task.quality.replace('p', '')
            ydl_opts['format'] = f'bestvideo[height<={h}]+bestaudio/best[height<={h}]/best'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([task.url])
            
            task.status = "Completed"
            if self.finished_callback and not task.is_cancelled:
                self.finished_callback(task.url, task.title, "Completed")
        except Exception as e:
            if str(e) == "Download cancelled by user":
                task.status = "Cancelled"
                if self.finished_callback:
                    self.finished_callback(task.url, task.title, "Cancelled")
            else:
                task.status = "Failed"
                if self.error_callback:
                    self.error_callback(task.url, task.title, str(e))

    def start_download(self, url, quality="1080p", title="Unknown Title"):
        if url in self.tasks:
            t = self.tasks[url]
            if t.status in ["Downloading", "Paused"]:
                return 
        
        task = DownloadTask(url, quality, title)
        task.status = "Downloading"
        self.tasks[url] = task
        
        task.thread = threading.Thread(
            target=self._download_task_runner, 
            args=(task,), 
            daemon=True
        )
        task.thread.start()

    def pause_download(self, url):
        if url in self.tasks:
            self.tasks[url].pause()

    def resume_download(self, url):
        if url in self.tasks:
            task = self.tasks[url]
            if task.status == "Paused":
                task.resume()
            elif task.status in ["Cancelled", "Failed"]:
                self.start_download(url, task.quality, task.title)

    def cancel_download(self, url=None):
        if url:
            if url in self.tasks:
                self.tasks[url].cancel()
        else:
            for task in self.tasks.values():
                if task.status in ["Downloading", "Paused"]:
                    task.cancel()

    def delete_download(self, url, title):
        safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        if not safe_title:
            safe_title = title
            
        pattern = os.path.join(self.download_folder, f"{safe_title}.*")
        files = glob.glob(pattern)
        
        if not files:
            for ext in ['.mp4', '.webm', '.mp3', '.m4a', '.mkv']:
                test_path = os.path.join(self.download_folder, f"{title}{ext}")
                if os.path.exists(test_path):
                    files.append(test_path)
                    
        for f in files:
            try:
                os.remove(f)
            except Exception as e:
                print(f"Error deleting {f}: {e}")
