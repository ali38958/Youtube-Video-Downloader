import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap import ScrolledFrame
from ttkbootstrap.dialogs import Messagebox
from PIL import Image, ImageTk
import threading
from tkinter import filedialog

from core.search import search_youtube, get_stream_url, download_thumbnail
from core.downloader import Downloader
from core.storage import load_settings, load_history, save_history
from ui.video_player import VideoPlayer

class MainWindow:
    def __init__(self, root):
        self.root = root
        
        self.settings = load_settings()
        self.history = load_history()
        
        self.downloader = Downloader(
            download_folder=self.settings.get('download_folder', ''),
            progress_callback=self.on_download_progress,
            finished_callback=self.on_download_finished,
            error_callback=self.on_download_error
        )
        
        self.thumbnail_cache = {} 
        self.current_video = None
        self.playing_video_url = None
        self.cards = {}
        
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(1, weight=1)
        
        # --- Top Navigation Bar ---
        self.top_frame = tb.Frame(self.root, padding=10, bootstyle="dark")
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        search_container = tb.Frame(self.top_frame, bootstyle="dark")
        search_container.pack(expand=True)
        
        tb.Label(search_container, text="URL / Search:", font=("Helvetica", 12, "bold"), bootstyle="inverse-dark").pack(side="left", padx=10)
        self.search_entry = tb.Entry(search_container, width=60, font=("Helvetica", 11))
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda e: self.do_search())
        
        self.search_btn = tb.Button(search_container, text="Search / Load", bootstyle="primary", command=self.do_search)
        self.search_btn.pack(side="left", padx=5)
        
        # --- Left Panel: Scrollable Results / History ---
        self.left_panel = tb.Frame(self.root, padding=10)
        self.left_panel.grid(row=1, column=0, sticky="nsew")
        
        self.notebook = tb.Notebook(self.left_panel)
        self.notebook.pack(fill="both", expand=True)
        
        # Results Tab
        self.results_tab = tb.Frame(self.notebook)
        self.notebook.add(self.results_tab, text="Search Results")
        self.results_frame = ScrolledFrame(self.results_tab, padding=5)
        self.results_frame.pack(fill="both", expand=True)
        
        # History Tab
        self.history_tab = tb.Frame(self.notebook)
        self.notebook.add(self.history_tab, text="Download History")
        self.history_frame = ScrolledFrame(self.history_tab, padding=5)
        self.history_frame.pack(fill="both", expand=True)
        self.load_history_ui()
        
        # --- Right Panel: Player & Details ---
        self.right_panel = tb.Frame(self.root, padding=10)
        self.right_panel.grid(row=1, column=1, sticky="nsew")
        
        self.video_player = VideoPlayer(self.right_panel, fullscreen_callback=self.toggle_fullscreen)
        self.video_player.pack(fill="both", expand=True)
        
        self.details_frame = tb.Frame(self.right_panel, padding=10)
        self.details_frame.pack(fill="x", pady=10)
        
        self.selected_title_var = tb.StringVar(value="Select a video to view details")
        tb.Label(self.details_frame, textvariable=self.selected_title_var, font=("Helvetica", 14, "bold"), wraplength=500).pack(anchor="w", pady=5)
        
        controls = tb.Frame(self.details_frame)
        controls.pack(fill="x", pady=5)
        
        tb.Label(controls, text="Quality:").pack(side="left", padx=5)
        self.format_var = tb.StringVar()
        self.format_combo = tb.Combobox(controls, textvariable=self.format_var, state="readonly", width=15)
        self.format_combo.pack(side="left", padx=5)
        
        self.download_btn = tb.Button(controls, text="Download", bootstyle="success", command=self.do_download, state="disabled")
        self.download_btn.pack(side="left", padx=5)
        
        self.watch_btn = tb.Button(controls, text="Watch Stream", bootstyle="primary", command=self.do_watch, state="disabled")
        self.watch_btn.pack(side="left", padx=5)
        
        # --- Bottom Panel: Settings ---
        self.bottom_panel = tb.Frame(self.root, padding=10, bootstyle="secondary")
        self.bottom_panel.grid(row=2, column=0, columnspan=2, sticky="ew")
        
        self.loc_btn = tb.Button(self.bottom_panel, text="Change Folder", bootstyle="info-outline", command=self.change_folder)
        self.loc_btn.pack(side="left", padx=5)
        
        self.status_var = tk.StringVar(value="Ready")
        tb.Label(self.bottom_panel, textvariable=self.status_var, bootstyle="inverse-secondary").pack(side="left", padx=10)
        
    def toggle_fullscreen(self, is_fullscreen):
        if is_fullscreen:
            self.top_frame.grid_remove()
            self.left_panel.grid_remove()
            self.bottom_panel.grid_remove()
            self.details_frame.pack_forget()
            self.right_panel.configure(padding=0)
        else:
            self.top_frame.grid()
            self.left_panel.grid()
            self.bottom_panel.grid()
            self.details_frame.pack(fill="x", pady=10)
            self.right_panel.configure(padding=10)
            
    def on_closing(self):
        active = False
        for t in self.downloader.tasks.values():
            if t.status in ["Downloading", "Paused"]:
                active = True
                break
                
        if active:
            if not Messagebox.yesno("Downloads are currently in progress.\nAre you sure you want to exit?", "Downloads Active"):
                return
            self.downloader.cancel_download()
        self.root.destroy()
        
    def change_folder(self):
        folder = filedialog.askdirectory(initialdir=self.settings.get('download_folder', ''))
        if folder:
            self.settings['download_folder'] = folder
            self.downloader.download_folder = folder
            save_settings(self.settings)
            self.status_var.set(f"Download folder changed to: {folder}")
            
    def load_history_ui(self):
        # We don't destroy all cards here easily if we want to preserve state, but recreating is fine.
        for widget in self.history_frame.winfo_children():
            widget.destroy()
            
        # Clean up card dictionary of history items
        to_del = [k for k, v in self.cards.items() if v.get("is_history")]
        for k in to_del: del self.cards[k]
            
        for item in self.history:
            self._create_card(self.history_frame, item, is_history=True)
            
    def do_search(self):
        query = self.search_entry.get().strip()
        if not query: return
            
        self.status_var.set("Searching...")
        self.search_btn.config(state="disabled")
        
        def search_thread():
            results = search_youtube(query)
            self.root.after(0, self.update_results_ui, results)
            
        threading.Thread(target=search_thread, daemon=True).start()
        
    def update_results_ui(self, results):
        self.search_btn.config(state="normal")
        self.status_var.set("Ready")
        
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        to_del = [k for k, v in self.cards.items() if not v.get("is_history")]
        for k in to_del: del self.cards[k]
            
        if not results:
            Messagebox.show_info("No results found.", "Search")
            return
            
        for r in results:
            self._create_card(self.results_frame, r, is_history=False)
            
        self.notebook.select(self.results_tab)
        
    def _create_card(self, parent, video_data, is_history=False):
        url = video_data.get('url', '')
        border_frame = tb.Frame(parent, bootstyle="secondary", padding=2)
        border_frame.pack(fill="x", pady=4, padx=4)
        
        card = tb.Frame(border_frame, bootstyle="dark", padding=5)
        card.pack(fill="both", expand=True)
        
        self.cards[url] = {
            "border": border_frame,
            "card": card,
            "data": video_data,
            "is_history": is_history
        }
        
        def on_select(e=None, v=video_data):
            self.select_video(v)
            
        border_frame.bind("<Button-1>", on_select)
        card.bind("<Button-1>", on_select)
        
        thumb_label = tb.Label(card, bootstyle="inverse-dark")
        thumb_label.pack(side="left", padx=5)
        thumb_label.bind("<Button-1>", on_select)
        
        thumb_url = video_data.get('thumbnail_url')
        if thumb_url:
            def load_thumb():
                path = download_thumbnail(thumb_url)
                if path:
                    self.root.after(0, lambda: self._set_image(thumb_label, path, url))
            threading.Thread(target=load_thumb, daemon=True).start()
            
        info_frame = tb.Frame(card, bootstyle="dark")
        info_frame.pack(side="left", fill="both", expand=True, padx=5)
        info_frame.bind("<Button-1>", on_select)
        
        title_lbl = tb.Label(info_frame, text=video_data.get('title', ''), font=("Helvetica", 10, "bold"), wraplength=250, bootstyle="inverse-dark")
        title_lbl.pack(anchor="w")
        title_lbl.bind("<Button-1>", on_select)
        
        if is_history:
            status_text = video_data.get('status', 'Completed')
            sub_lbl = tb.Label(info_frame, text=f"Status: {status_text}", bootstyle="inverse-dark")
            sub_lbl.pack(anchor="w", pady=2)
            sub_lbl.bind("<Button-1>", on_select)
            
            # History Controls
            history_controls = tb.Frame(info_frame, bootstyle="dark")
            history_controls.pack(fill="x", pady=5)
            
            progress = tb.Progressbar(history_controls, orient="horizontal", mode="determinate", bootstyle="success-striped")
            
            action_btn = tb.Button(history_controls, text="Delete", bootstyle="danger-outline")
            cancel_btn = tb.Button(history_controls, text="Cancel", bootstyle="danger")
            
            self.cards[url]["progress"] = progress
            self.cards[url]["action_btn"] = action_btn
            self.cards[url]["cancel_btn"] = cancel_btn
            self.cards[url]["status_lbl"] = sub_lbl
            
            self._update_card_state(url, status_text)
            
        else:
            sub_lbl = tb.Label(info_frame, text=f"{video_data.get('uploader', '')} • {video_data.get('duration', '')}", bootstyle="inverse-dark")
            sub_lbl.pack(anchor="w", pady=2)
            sub_lbl.bind("<Button-1>", on_select)
        
        url_lbl = tb.Label(info_frame, text=url, font=("Helvetica", 8), bootstyle="secondary", wraplength=250)
        url_lbl.pack(anchor="w")
        url_lbl.bind("<Button-1>", on_select)

    def _update_card_state(self, url, status):
        card = self.cards.get(url)
        if not card or "action_btn" not in card: return
        
        card["status_lbl"].config(text=f"Status: {status}")
        
        # Detach all first
        card["progress"].pack_forget()
        card["action_btn"].pack_forget()
        card["cancel_btn"].pack_forget()
        
        if status == "Downloading":
            card["progress"].pack(side="left", fill="x", expand=True, padx=(0, 5))
            card["action_btn"].config(text="Pause", bootstyle="warning", command=lambda: self.do_pause(url))
            card["action_btn"].pack(side="left", padx=2)
            card["cancel_btn"].config(command=lambda: self.do_cancel_item(url))
            card["cancel_btn"].pack(side="left", padx=2)
            
        elif status == "Paused":
            card["progress"].pack(side="left", fill="x", expand=True, padx=(0, 5))
            card["action_btn"].config(text="Resume", bootstyle="success", command=lambda: self.do_resume(url))
            card["action_btn"].pack(side="left", padx=2)
            card["cancel_btn"].config(command=lambda: self.do_cancel_item(url))
            card["cancel_btn"].pack(side="left", padx=2)
            
        else: # Completed, Cancelled, Failed
            card["action_btn"].config(text="Delete", bootstyle="danger-outline", command=lambda: self.do_delete(url))
            card["action_btn"].pack(side="left", padx=2)

    def _update_borders(self):
        for k, v in self.cards.items():
            if k == self.playing_video_url:
                v["border"].configure(bootstyle="success")
            elif self.current_video and k == self.current_video.get('url'):
                v["border"].configure(bootstyle="primary")
            else:
                v["border"].configure(bootstyle="secondary")

    def do_pause(self, url):
        self.downloader.pause_download(url)
        self._update_card_state(url, "Paused")
        self._update_history_status(url, "Paused")

    def do_resume(self, url):
        self.downloader.resume_download(url)
        self._update_card_state(url, "Downloading")
        self._update_history_status(url, "Downloading")
        
    def do_cancel_item(self, url):
        self.downloader.cancel_download(url)
        self._update_card_state(url, "Cancelled")
        self._update_history_status(url, "Cancelled")
        
    def do_delete(self, url):
        if Messagebox.yesno("Delete this video from history and disk?", "Confirm Delete"):
            title = "Unknown"
            to_remove = None
            for item in self.history:
                if item['url'] == url:
                    title = item['title']
                    to_remove = item
                    break
            if to_remove:
                self.history.remove(to_remove)
                save_history(self.history)
                
            self.downloader.delete_download(url, title)
            self.load_history_ui()

    def _update_history_status(self, url, status):
        for item in self.history:
            if item['url'] == url:
                item['status'] = status
                break
        save_history(self.history)

    def _set_image(self, label, path, key):
        try:
            img = Image.open(path)
            img.thumbnail((120, 90))
            photo = ImageTk.PhotoImage(img)
            self.thumbnail_cache[key] = photo
            label.config(image=photo)
        except Exception:
            pass

    def select_video(self, video_data):
        self.current_video = video_data
        self._update_borders()
        self.selected_title_var.set(video_data.get('title', 'Unknown'))
        
        self.watch_btn.config(state="normal")
        self.download_btn.config(state="disabled")
        self.format_var.set("")
        self.format_combo['values'] = []
        
        self.do_fetch_formats()

    def do_fetch_formats(self):
        if not self.current_video: return
        self.status_var.set("Fetching available qualities...")
        self.format_combo.set("Loading...")
        
        def fetch_thread():
            formats = self.downloader.fetch_formats(self.current_video['url'])
            self.root.after(0, lambda: self._on_formats_fetched(formats))
            
        threading.Thread(target=fetch_thread, daemon=True).start()
        
    def _on_formats_fetched(self, formats):
        self.status_var.set("Qualities loaded. Ready to download.")
        if formats:
            self.format_combo['values'] = formats
            self.format_var.set(formats[0])
            self.download_btn.config(state="normal")
            
    def do_download(self):
        if not self.current_video or not self.format_var.get(): return
        
        title = self.current_video['title']
        url = self.current_video['url']
        quality = self.format_var.get()
        
        self.status_var.set(f"Download queued: {title}")
        
        exists = False
        for item in self.history:
            if item['url'] == url:
                item['status'] = 'Downloading'
                exists = True
                break
        if not exists:
            self.history.insert(0, {'title': title, 'url': url, 'status': 'Downloading', 'thumbnail_url': self.current_video.get('thumbnail_url')})
        save_history(self.history)
        
        self.load_history_ui()
        self.notebook.select(self.history_tab)
        
        self.downloader.start_download(url, quality, title)

    def do_watch(self):
        if not self.current_video: return
        self.status_var.set(f"Loading stream: {self.current_video['title']}")
        url = self.current_video['url']
        
        self.playing_video_url = url
        self._update_borders()
        
        def load_stream_thread():
            stream_url = get_stream_url(url)
            if stream_url:
                self.root.after(0, lambda: self.video_player.load_media(stream_url))
                self.root.after(0, lambda: self.status_var.set(f"Playing: {self.current_video['title']}"))
            else:
                self.root.after(0, lambda: self.status_var.set("Failed to load stream"))
                
        threading.Thread(target=load_stream_thread, daemon=True).start()

    def on_download_progress(self, url, percent_str, speed_str):
        def update():
            self.status_var.set(f"Downloading active items...")
            card = self.cards.get(url)
            if card and "progress" in card:
                try:
                    val = float(percent_str.strip('%').strip())
                    card["progress"]['value'] = val
                    card["status_lbl"].config(text=f"Status: Downloading... {percent_str} at {speed_str}")
                except ValueError:
                    pass
        self.root.after(0, update)

    def on_download_finished(self, url, title, status):
        def update():
            self.status_var.set(f"{title} - {status}")
            self._update_history_status(url, status)
            self._update_card_state(url, status)
            
            if status == "Completed":
                Messagebox.show_info(f"Successfully downloaded:\n{title}", "Complete")
            elif status == "Cancelled":
                Messagebox.show_warning(f"Download was cancelled:\n{title}", "Cancelled")
                
        self.root.after(0, update)

    def on_download_error(self, url, title, error_msg):
        def update():
            self.status_var.set("Download Error")
            self._update_history_status(url, "Failed")
            self._update_card_state(url, "Failed")
            Messagebox.show_error(f"Failed to download {title}.\nError: {error_msg}", "Error")
            
        self.root.after(0, update)
