import tkinter as tk
from tkinter import ttk, filedialog
import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox
from PIL import Image, ImageTk
import threading
import os
import subprocess

from core.search import search_youtube, get_stream_url, download_thumbnail
from core.downloader import Downloader
from core.storage import load_settings, save_settings, load_history, save_history
from ui.video_player import VideoPlayer
from ui.theme import theme_mgr, THEMES

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
        self.cards = {}
        self.current_tab = "results"  # "results" or "history"
        
        # Animation state flags
        self._is_searching = False
        self._search_anim_frame = 0
        self._is_extracting_stream = False
        self._stream_anim_frame = 0
        
        self.setup_ui()
        
        # Register theme listener
        theme_mgr.register_listener(self.apply_theme)
        
        # Apply initial theme
        self.apply_theme(theme_mgr.current_theme)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        # Configure root layout
        self.root.columnconfigure(0, weight=1, minsize=420)
        self.root.columnconfigure(1, weight=2, minsize=500)
        self.root.rowconfigure(1, weight=1)
        
        # --- 1. TOP COMMAND HEADER ---
        self.top_frame = tk.Frame(self.root, padx=12, pady=10)
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        # Branding Tag with App Icon
        self.brand_frame = tk.Frame(self.top_frame, padx=8, pady=4, relief="solid", bd=2)
        self.brand_frame.pack(side="left", padx=(0, 12))
        
        self.logo_photo = None
        self.logo_label = tk.Label(self.brand_frame, bd=0)
        self.logo_label.pack(side="left", padx=(0, 6))
        self._update_logo_image(theme_mgr.current_theme)
                
        self.brand_label = tk.Label(
            self.brand_frame, 
            text="YT // RAW LOADER", 
            font=theme_mgr.get_font("brand")
        )
        self.brand_label.pack(side="left")
        
        # Search Container
        self.search_container = tk.Frame(self.top_frame, relief="solid", bd=2, padx=4, pady=3)
        self.search_container.pack(side="left", fill="x", expand=True, padx=4)
        
        self.search_prompt_label = tk.Label(
            self.search_container, 
            text="INPUT //", 
            font=theme_mgr.get_font("mono_bold")
        )
        self.search_prompt_label.pack(side="left", padx=(4, 6))
        
        self.search_entry = tk.Entry(
            self.search_container, 
            font=theme_mgr.get_font("mono"),
            relief="flat",
            bd=0
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=4)
        self.search_entry.bind("<Return>", lambda e: self.do_search())
        
        self.search_btn = tk.Button(
            self.top_frame,
            text="[ ⚡ SEARCH ]",
            font=theme_mgr.get_font("mono_bold"),
            relief="solid",
            bd=2,
            cursor="hand2",
            padx=14,
            pady=4,
            command=self.do_search
        )
        self.search_btn.pack(side="left", padx=(6, 12))
        
        # Theme Switcher Selector
        self.theme_frame = tk.Frame(self.top_frame, relief="solid", bd=2, padx=6, pady=3)
        self.theme_frame.pack(side="right", padx=(4, 0))
        
        self.theme_lbl = tk.Label(
            self.theme_frame, 
            text="THEME:", 
            font=theme_mgr.get_font("mono_bold")
        )
        self.theme_lbl.pack(side="left", padx=(0, 4))
        
        theme_names = [t["name"] for t in THEMES.values()]
        current_name = theme_mgr.current_theme["name"]
        
        self.theme_var = tk.StringVar(value=current_name)
        self.theme_combo = ttk.Combobox(
            self.theme_frame,
            textvariable=self.theme_var,
            values=theme_names,
            state="readonly",
            width=13,
            font=theme_mgr.get_font("mono_sm")
        )
        self.theme_combo.pack(side="left")
        self.theme_combo.bind("<<ComboboxSelected>>", self.on_theme_selected)
        
        # --- 2. LEFT PANEL: FEED & HISTORY ---
        self.left_panel = tk.Frame(self.root, padx=10, pady=8)
        self.left_panel.grid(row=1, column=0, sticky="nsew")
        self.left_panel.rowconfigure(1, weight=1)
        self.left_panel.columnconfigure(0, weight=1)
        
        # Brutalist Segmented Tab Selector
        self.tab_bar = tk.Frame(self.left_panel, relief="solid", bd=2, padx=2, pady=2)
        self.tab_bar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.tab_bar.columnconfigure(0, weight=1)
        self.tab_bar.columnconfigure(1, weight=1)
        
        self.tab_results_btn = tk.Button(
            self.tab_bar,
            text="[ 01 // RESULTS ]",
            font=theme_mgr.get_font("mono_bold"),
            relief="solid",
            bd=1,
            cursor="hand2",
            pady=4,
            command=lambda: self.switch_tab("results")
        )
        self.tab_results_btn.grid(row=0, column=0, sticky="ew", padx=1)
        
        self.tab_history_btn = tk.Button(
            self.tab_bar,
            text="[ 02 // QUEUE & HISTORY ]",
            font=theme_mgr.get_font("mono_bold"),
            relief="solid",
            bd=1,
            cursor="hand2",
            pady=4,
            command=lambda: self.switch_tab("history")
        )
        self.tab_history_btn.grid(row=0, column=1, sticky="ew", padx=1)
        
        # Scrollable Container for Results / History
        self.feed_canvas_container = tk.Frame(self.left_panel, relief="solid", bd=2)
        self.feed_canvas_container.grid(row=1, column=0, sticky="nsew")
        self.feed_canvas_container.rowconfigure(0, weight=1)
        self.feed_canvas_container.columnconfigure(0, weight=1)
        
        self.feed_canvas = tk.Canvas(self.feed_canvas_container, bd=0, highlightthickness=0)
        self.feed_scrollbar = ttk.Scrollbar(self.feed_canvas_container, orient="vertical", command=self.feed_canvas.yview)
        self.feed_scrollable_frame = tk.Frame(self.feed_canvas)
        
        self.feed_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.feed_canvas.configure(scrollregion=self.feed_canvas.bbox("all"))
        )
        
        self.feed_window_id = self.feed_canvas.create_window((0, 0), window=self.feed_scrollable_frame, anchor="nw")
        self.feed_canvas.bind("<Configure>", lambda e: self.feed_canvas.itemconfig(self.feed_window_id, width=e.width))
        
        self.feed_canvas.configure(yscrollcommand=self.feed_scrollbar.set)
        
        self.feed_canvas.grid(row=0, column=0, sticky="nsew")
        self.feed_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Mousewheel scroll support
        self._bind_mousewheel(self.feed_canvas)
        self._bind_mousewheel(self.feed_scrollable_frame)
        
        # --- 3. RIGHT PANEL: MEDIA STATION & COMMAND DECK ---
        self.right_panel = tk.Frame(self.root, padx=10, pady=8)
        self.right_panel.grid(row=1, column=1, sticky="nsew")
        self.right_panel.rowconfigure(0, weight=1)
        self.right_panel.columnconfigure(0, weight=1)
        
        # Video Player Frame
        self.video_player = VideoPlayer(self.right_panel, fullscreen_callback=self.toggle_fullscreen)
        self.video_player.grid(row=0, column=0, sticky="nsew")
        
        # Video Details & Downloader Action Station
        self.details_box = tk.Frame(self.right_panel, relief="solid", bd=2, padx=12, pady=10)
        self.details_box.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        
        self.selected_title_var = tk.StringVar(value="[ NO VIDEO SELECTED // SEARCH OR PASTE URL ]")
        self.selected_title_label = tk.Label(
            self.details_box,
            textvariable=self.selected_title_var,
            font=theme_mgr.get_font("title"),
            anchor="w",
            justify="left",
            wraplength=550
        )
        self.selected_title_label.pack(fill="x", pady=(0, 8))
        
        # Controls Row
        self.action_row = tk.Frame(self.details_box)
        self.action_row.pack(fill="x")
        
        self.quality_lbl = tk.Label(
            self.action_row, 
            text="QUALITY:", 
            font=theme_mgr.get_font("mono_bold")
        )
        self.quality_lbl.pack(side="left", padx=(0, 6))
        
        self.format_var = tk.StringVar(value=self.settings.get("default_quality", "1080p"))
        self.format_combo = ttk.Combobox(
            self.action_row,
            textvariable=self.format_var,
            values=["1080p", "720p", "480p", "360p", "Audio Only"],
            state="readonly",
            width=12,
            font=theme_mgr.get_font("mono_sm")
        )
        self.format_combo.pack(side="left", padx=(0, 12))
        
        self.download_btn = tk.Button(
            self.action_row,
            text="[ ⬇ DOWNLOAD VIDEO ]",
            font=theme_mgr.get_font("mono_bold"),
            relief="solid",
            bd=2,
            cursor="hand2",
            padx=14,
            pady=4,
            state="disabled",
            command=self.do_download
        )
        self.download_btn.pack(side="left", padx=(0, 8))
        
        self.watch_btn = tk.Button(
            self.action_row,
            text="[ ⚡ STREAM LIVE ]",
            font=theme_mgr.get_font("mono_bold"),
            relief="solid",
            bd=2,
            cursor="hand2",
            padx=12,
            pady=4,
            state="disabled",
            command=self.do_watch
        )
        self.watch_btn.pack(side="left")
        
        # --- 4. BOTTOM STATUS / TELEMETRY BAR ---
        self.bottom_panel = tk.Frame(self.root, relief="solid", bd=2, padx=10, pady=6)
        self.bottom_panel.grid(row=2, column=0, columnspan=2, sticky="ew")
        
        self.loc_btn = tk.Button(
            self.bottom_panel,
            text="[ 📁 FOLDER ]",
            font=theme_mgr.get_font("mono_bold"),
            relief="solid",
            bd=1,
            cursor="hand2",
            padx=8,
            pady=2,
            command=self.change_folder
        )
        self.loc_btn.pack(side="left", padx=(0, 8))
        
        self.dest_label = tk.Label(
            self.bottom_panel,
            text=f"PATH: {self.settings.get('download_folder', 'Downloads')}",
            font=theme_mgr.get_font("mono_sm")
        )
        self.dest_label.pack(side="left", padx=(0, 16))
        
        self.status_var = tk.StringVar(value="[ ENGINE: READY ]")
        self.status_label = tk.Label(
            self.bottom_panel,
            textvariable=self.status_var,
            font=theme_mgr.get_font("mono_bold")
        )
        self.status_label.pack(side="right")
        
        # Load initial history data
        self.render_history_cards()

    def _bind_mousewheel(self, widget):
        def _on_mousewheel(event):
            self.feed_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        widget.bind("<MouseWheel>", _on_mousewheel)

    def on_theme_selected(self, event=None):
        selected_name = self.theme_var.get()
        for t_id, t_data in THEMES.items():
            if t_data["name"] == selected_name:
                theme_mgr.set_theme(t_id)
                break

    def _update_logo_image(self, theme):
        logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png")
        if os.path.exists(logo_path) and hasattr(self, "logo_label") and self.logo_label:
            try:
                raw_img = Image.open(logo_path).convert("RGBA").resize((28, 28), Image.Resampling.LANCZOS)
                bg_color = theme.get("accent_primary", "#FFE600")
                h = bg_color.lstrip("#")
                if len(h) == 6:
                    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
                else:
                    rgb = (255, 230, 0)
                bg_img = Image.new("RGBA", (28, 28), rgb + (255,))
                composited = Image.alpha_composite(bg_img, raw_img)
                self.logo_photo = ImageTk.PhotoImage(composited)
                self.logo_label.configure(image=self.logo_photo, bg=bg_color)
            except Exception as e:
                print(f"Error updating logo image: {e}")

    def apply_theme(self, theme):
        try:
            self.root.configure(bg=theme["bg_canvas"])
            
            # Top Frame
            self.top_frame.configure(bg=theme["bg_surface"])
            self.brand_frame.configure(bg=theme["accent_primary"], highlightbackground=theme["border_bold"])
            self.brand_label.configure(bg=theme["accent_primary"], fg=theme["text_on_accent"])
            self._update_logo_image(theme)
            
            self.search_container.configure(bg=theme["bg_sunken"], highlightbackground=theme["border_bold"])
            self.search_prompt_label.configure(bg=theme["bg_sunken"], fg=theme["accent_primary"])
            self.search_entry.configure(
                bg=theme["bg_sunken"], 
                fg=theme["text_primary"], 
                insertbackground=theme["accent_primary"]
            )
            self.search_btn.configure(
                bg=theme["accent_primary"], 
                fg=theme["text_on_accent"],
                activebackground=theme["accent_secondary"]
            )
            
            self.theme_frame.configure(bg=theme["bg_surface_elevated"], highlightbackground=theme["border_bold"])
            self.theme_lbl.configure(bg=theme["bg_surface_elevated"], fg=theme["text_secondary"])
            
            # Left Panel
            self.left_panel.configure(bg=theme["bg_canvas"])
            self.tab_bar.configure(bg=theme["bg_surface"], highlightbackground=theme["border_bold"])
            self.feed_canvas_container.configure(bg=theme["border_bold"])
            self.feed_canvas.configure(bg=theme["bg_canvas"])
            self.feed_scrollable_frame.configure(bg=theme["bg_canvas"])
            
            self.update_tab_buttons(theme)
            
            # Right Panel
            self.right_panel.configure(bg=theme["bg_canvas"])
            self.details_box.configure(bg=theme["bg_surface"], highlightbackground=theme["border_bold"])
            self.selected_title_label.configure(bg=theme["bg_surface"], fg=theme["text_primary"])
            self.action_row.configure(bg=theme["bg_surface"])
            self.quality_lbl.configure(bg=theme["bg_surface"], fg=theme["text_secondary"])
            
            self.download_btn.configure(
                bg=theme["accent_primary"],
                fg=theme["text_on_accent"],
                activebackground=theme["accent_success"]
            )
            self.watch_btn.configure(
                bg=theme["accent_secondary"],
                fg=theme["text_on_accent"],
                activebackground=theme["accent_primary"]
            )
            
            # Bottom Panel
            self.bottom_panel.configure(bg=theme["bg_surface"], highlightbackground=theme["border_bold"])
            self.loc_btn.configure(
                bg=theme["bg_surface_elevated"],
                fg=theme["text_primary"],
                activebackground=theme["accent_primary"],
                activeforeground=theme["text_on_accent"]
            )
            self.dest_label.configure(bg=theme["bg_surface"], fg=theme["text_secondary"])
            self.status_label.configure(bg=theme["bg_surface"], fg=theme["accent_secondary"])
            
            # Refresh rendered feed cards with new colors
            if self.current_tab == "results":
                self.reapply_card_styles(theme)
            else:
                self.render_history_cards()
                
        except Exception as e:
            print(f"Error applying theme in MainWindow: {e}")

    def update_tab_buttons(self, theme=None):
        if not theme:
            theme = theme_mgr.current_theme
            
        if self.current_tab == "results":
            self.tab_results_btn.configure(
                bg=theme["accent_primary"],
                fg=theme["text_on_accent"],
                activebackground=theme["accent_primary"]
            )
            self.tab_history_btn.configure(
                bg=theme["bg_surface_elevated"],
                fg=theme["text_secondary"],
                activebackground=theme["bg_surface"]
            )
        else:
            self.tab_results_btn.configure(
                bg=theme["bg_surface_elevated"],
                fg=theme["text_secondary"],
                activebackground=theme["bg_surface"]
            )
            self.tab_history_btn.configure(
                bg=theme["accent_primary"],
                fg=theme["text_on_accent"],
                activebackground=theme["accent_primary"]
            )

    def switch_tab(self, tab_name):
        self.current_tab = tab_name
        self.update_tab_buttons()
        
        for widget in self.feed_scrollable_frame.winfo_children():
            widget.destroy()
        self.cards.clear()
        
        if tab_name == "results":
            self.status_var.set("[ MODE: SEARCH RESULTS ]")
            if hasattr(self, "last_search_results") and self.last_search_results:
                for r in self.last_search_results:
                    self._create_card(r, is_history=False)
            else:
                empty_lbl = tk.Label(
                    self.feed_scrollable_frame,
                    text="[ NO SEARCH RESULTS // ENTER QUERY OR URL ABOVE ]",
                    font=theme_mgr.get_font("mono_bold"),
                    fg=theme_mgr.get("text_muted"),
                    bg=theme_mgr.get("bg_canvas"),
                    pady=40
                )
                empty_lbl.pack()
        else:
            self.status_var.set("[ MODE: DOWNLOAD QUEUE & HISTORY ]")
            self.render_history_cards()

    def toggle_fullscreen(self, is_fullscreen):
        if is_fullscreen:
            self.root.attributes("-fullscreen", True)
            self.top_frame.grid_remove()
            self.left_panel.grid_remove()
            self.bottom_panel.grid_remove()
            self.details_box.grid_remove()
            
            # Expand root grid columns and rows to 100%
            self.root.columnconfigure(0, weight=1, minsize=0)
            self.root.columnconfigure(1, weight=0, minsize=0)
            self.root.rowconfigure(0, weight=1)
            self.root.rowconfigure(1, weight=0)
            self.root.rowconfigure(2, weight=0)
            
            self.right_panel.configure(padx=0, pady=0)
            self.right_panel.grid(row=0, column=0, columnspan=2, rowspan=3, sticky="nsew")
        else:
            self.root.attributes("-fullscreen", False)
            # Restore multi-pane grid configuration
            self.root.columnconfigure(0, weight=1, minsize=420)
            self.root.columnconfigure(1, weight=2, minsize=500)
            self.root.rowconfigure(0, weight=0)
            self.root.rowconfigure(1, weight=1)
            self.root.rowconfigure(2, weight=0)
            
            self.top_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
            self.left_panel.grid(row=1, column=0, sticky="nsew")
            self.right_panel.grid(row=1, column=1, sticky="nsew")
            self.details_box.grid(row=1, column=0, sticky="ew", pady=(10, 0))
            self.bottom_panel.grid(row=2, column=0, columnspan=2, sticky="ew")
            self.right_panel.configure(padx=10, pady=8)

    def on_closing(self):
        active = any(t.status in ["Downloading", "Paused"] for t in self.downloader.tasks.values())
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
            self.dest_label.config(text=f"PATH: {folder}")
            self.status_var.set(f"[ FOLDER UPDATED // {os.path.basename(folder)} ]")

    # --- Animated Search Workflow ---
    def do_search(self):
        query = self.search_entry.get().strip()
        if not query:
            return
            
        self._is_searching = True
        self._search_anim_frame = 0
        self.search_btn.config(text="[ ⏳ SCANNING... ]", state="disabled")
        
        # Render animated radar card in feed
        for widget in self.feed_scrollable_frame.winfo_children():
            widget.destroy()
            
        theme = theme_mgr.current_theme
        self.search_anim_card = tk.Frame(
            self.feed_scrollable_frame,
            bg=theme["border_active"],
            relief="solid",
            bd=2,
            padx=1,
            pady=1
        )
        self.search_anim_card.pack(fill="x", padx=12, pady=20)
        
        self.search_anim_inner = tk.Frame(
            self.search_anim_card,
            bg=theme["bg_surface"],
            padx=16,
            pady=16
        )
        self.search_anim_inner.pack(fill="both", expand=True)
        
        self.search_radar_title = tk.Label(
            self.search_anim_inner,
            text=f"[ ⚡ SCANNING: \"{query[:30]}\" ]",
            font=theme_mgr.get_font("mono_bold"),
            fg=theme["accent_primary"],
            bg=theme["bg_surface"]
        )
        self.search_radar_title.pack(pady=(0, 6))
        
        self.search_radar_bar = tk.Label(
            self.search_anim_inner,
            text="[ ■■□□□□□□□□ ]",
            font=theme_mgr.get_font("mono_bold"),
            fg=theme["accent_secondary"],
            bg=theme["bg_surface"]
        )
        self.search_radar_bar.pack(pady=(0, 4))
        
        self.search_radar_sub = tk.Label(
            self.search_anim_inner,
            text="CONNECTING TO YOUTUBE ENGINE...",
            font=theme_mgr.get_font("mono_xs"),
            fg=theme["text_secondary"],
            bg=theme["bg_surface"]
        )
        self.search_radar_sub.pack()
        
        self._animate_search_loop()
        
        def search_thread():
            results = search_youtube(query)
            self.root.after(0, self.update_results_ui, results)
            
        threading.Thread(target=search_thread, daemon=True).start()

    def _animate_search_loop(self):
        if not self._is_searching:
            return
            
        blocks = [
            "[ ■■□□□□□□□□ ]",
            "[ □■■□□□□□□□ ]",
            "[ □□■■□□□□□□ ]",
            "[ □□□■■□□□□□ ]",
            "[ □□□□■■□□□□ ]",
            "[ □□□□□■■□□□ ]",
            "[ □□□□□□■■□□ ]",
            "[ □□□□□□□■■□ ]",
            "[ □□□□□□□□■■ ]",
            "[ ■□□□□□□□□■ ]"
        ]
        status_spinners = ["▰▱▱▱▱", "▰▰▱▱▱", "▰▰▰▱▱", "▰▰▰▰▱", "▰▰▰▰▰"]
        
        self._search_anim_frame += 1
        b_idx = self._search_anim_frame % len(blocks)
        s_idx = self._search_anim_frame % len(status_spinners)
        
        if hasattr(self, "search_radar_bar") and self.search_radar_bar.winfo_exists():
            self.search_radar_bar.config(text=blocks[b_idx])
            
        self.status_var.set(f"[ SCANNING YOUTUBE {status_spinners[s_idx]} ]")
        self.root.after(100, self._animate_search_loop)

    def update_results_ui(self, results):
        self._is_searching = False
        self.search_btn.config(text="[ ⚡ SEARCH ]", state="normal")
        self.status_var.set(f"[ FOUND {len(results)} ITEMS ]")
        self.last_search_results = results
        
        self.switch_tab("results")

    def _create_card(self, video_data, is_history=False):
        url = video_data.get('url', '')
        theme = theme_mgr.current_theme
        
        # Outer border frame
        border_frame = tk.Frame(
            self.feed_scrollable_frame,
            bg=theme["border_bold"],
            relief="solid",
            bd=2,
            padx=1,
            pady=1
        )
        border_frame.pack(fill="x", padx=6, pady=4)
        
        # Inner card frame
        card = tk.Frame(
            border_frame,
            bg=theme["bg_surface"],
            padx=6,
            pady=6
        )
        card.pack(fill="both", expand=True)
        
        card_entry = {
            "border": border_frame,
            "card": card,
            "data": video_data,
            "is_history": is_history,
            "labels": [],
            "buttons": []
        }
        self.cards[url] = card_entry
        
        def on_select(e=None, v=video_data):
            self.select_video(v)
            
        border_frame.bind("<Button-1>", on_select)
        card.bind("<Button-1>", on_select)
        self._bind_mousewheel(border_frame)
        self._bind_mousewheel(card)
        
        # Thumbnail Box with Duration Badge
        thumb_container = tk.Frame(card, bg=theme["bg_sunken"], relief="solid", bd=1)
        thumb_container.pack(side="left", padx=(2, 8))
        thumb_container.bind("<Button-1>", on_select)
        self._bind_mousewheel(thumb_container)
        
        thumb_label = tk.Label(thumb_container, bg=theme["bg_sunken"], text="[ NO IMG ]", font=theme_mgr.get_font("mono_xs"), fg=theme["text_muted"], width=14, height=4)
        thumb_label.pack()
        thumb_label.bind("<Button-1>", on_select)
        self._bind_mousewheel(thumb_label)
        
        thumb_url = video_data.get('thumbnail_url')
        if thumb_url:
            def load_thumb():
                path = download_thumbnail(thumb_url)
                if path:
                    self.root.after(0, lambda: self._set_image(thumb_label, path, url))
            threading.Thread(target=load_thumb, daemon=True).start()
            
        # Metadata Information Column
        info_frame = tk.Frame(card, bg=theme["bg_surface"])
        info_frame.pack(side="left", fill="both", expand=True)
        info_frame.bind("<Button-1>", on_select)
        self._bind_mousewheel(info_frame)
        
        # Title
        title_text = video_data.get('title', 'Unknown Title')
        title_lbl = tk.Label(
            info_frame,
            text=title_text,
            font=theme_mgr.get_font("body_bold"),
            fg=theme["text_primary"],
            bg=theme["bg_surface"],
            anchor="w",
            justify="left",
            wraplength=220
        )
        title_lbl.pack(anchor="w")
        title_lbl.bind("<Button-1>", on_select)
        self._bind_mousewheel(title_lbl)
        card_entry["labels"].append(title_lbl)
        
        # Sub-info row (Duration / Channel)
        sub_frame = tk.Frame(info_frame, bg=theme["bg_surface"])
        sub_frame.pack(anchor="w", fill="x", pady=(2, 4))
        sub_frame.bind("<Button-1>", on_select)
        self._bind_mousewheel(sub_frame)
        
        duration_text = f"[ {video_data.get('duration', '--:--')} ]"
        dur_badge = tk.Label(
            sub_frame,
            text=duration_text,
            font=theme_mgr.get_font("mono_xs"),
            bg=theme["bg_sunken"],
            fg=theme["accent_primary"],
            relief="solid",
            bd=1,
            padx=4,
            pady=1
        )
        dur_badge.pack(side="left", padx=(0, 6))
        dur_badge.bind("<Button-1>", on_select)
        self._bind_mousewheel(dur_badge)
        
        uploader_text = video_data.get('uploader', '')
        if uploader_text:
            up_lbl = tk.Label(
                sub_frame,
                text=uploader_text,
                font=theme_mgr.get_font("mono_xs"),
                fg=theme["text_secondary"],
                bg=theme["bg_surface"]
            )
            up_lbl.pack(side="left")
            up_lbl.bind("<Button-1>", on_select)
            self._bind_mousewheel(up_lbl)
            card_entry["labels"].append(up_lbl)
            
        if is_history:
            status_text = video_data.get('status', 'Completed')
            
            status_badge = tk.Label(
                info_frame,
                text=f"STATUS: {status_text.upper()}",
                font=theme_mgr.get_font("mono_xs"),
                bg=theme["bg_surface_elevated"],
                fg=theme["accent_success"] if status_text == "Completed" else theme["accent_primary"],
                relief="solid",
                bd=1,
                padx=4,
                pady=1
            )
            status_badge.pack(anchor="w", pady=(2, 4))
            
            # Progress Bar for Downloading tasks
            progress = ttk.Progressbar(info_frame, orient="horizontal", mode="determinate")
            progress.pack(fill="x", pady=2)
            
            speed_lbl = tk.Label(
                info_frame,
                text=video_data.get('speed', '0 KB/s'),
                font=theme_mgr.get_font("mono_xs"),
                fg=theme["text_muted"],
                bg=theme["bg_surface"]
            )
            speed_lbl.pack(anchor="w")
            card_entry["labels"].append(speed_lbl)
            
            # History Controls Row
            ctrl_row = tk.Frame(info_frame, bg=theme["bg_surface"])
            ctrl_row.pack(fill="x", pady=(4, 0))
            
            delete_btn = tk.Button(
                ctrl_row,
                text="[ 🗑 REMOVE ]",
                font=theme_mgr.get_font("mono_xs"),
                bg=theme["bg_surface_elevated"],
                fg=theme["accent_danger"],
                relief="solid",
                bd=1,
                cursor="hand2",
                command=lambda: self.delete_history_item(url)
            )
            delete_btn.pack(side="left", padx=(0, 4))
            card_entry["buttons"].append(delete_btn)
            
            # Open folder button if completed
            if status_text == "Completed":
                open_btn = tk.Button(
                    ctrl_row,
                    text="[ 📂 OPEN ]",
                    font=theme_mgr.get_font("mono_xs"),
                    bg=theme["bg_surface_elevated"],
                    fg=theme["accent_primary"],
                    relief="solid",
                    bd=1,
                    cursor="hand2",
                    command=lambda: self.open_download_folder()
                )
                open_btn.pack(side="left")
                card_entry["buttons"].append(open_btn)
                
            card_entry["progress"] = progress
            card_entry["speed_lbl"] = speed_lbl
            card_entry["status_badge"] = status_badge
        else:
            # Result Quick Stream Button
            quick_btn_row = tk.Frame(info_frame, bg=theme["bg_surface"])
            quick_btn_row.pack(anchor="w", fill="x", pady=(2, 0))
            
            stream_btn = tk.Button(
                quick_btn_row,
                text="[ ⚡ STREAM ]",
                font=theme_mgr.get_font("mono_xs"),
                bg=theme["bg_surface_elevated"],
                fg=theme["accent_secondary"],
                relief="solid",
                bd=1,
                cursor="hand2",
                command=lambda: self.quick_stream(video_data)
            )
            stream_btn.pack(side="left", padx=(0, 6))
            card_entry["buttons"].append(stream_btn)

    def _set_image(self, label, path, url):
        try:
            img = Image.open(path)
            img = img.resize((100, 60), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.thumbnail_cache[url] = photo
            label.config(image=photo, text="", width=100, height=60)
        except Exception:
            pass

    def reapply_card_styles(self, theme):
        for url, item in self.cards.items():
            is_active = (self.current_video and self.current_video.get('url') == url)
            item["border"].configure(bg=theme["border_active"] if is_active else theme["border_bold"])
            item["card"].configure(bg=theme["bg_surface"])
            for lbl in item.get("labels", []):
                lbl.configure(bg=theme["bg_surface"], fg=theme["text_primary"])
            for btn in item.get("buttons", []):
                btn.configure(bg=theme["bg_surface_elevated"])

    def select_video(self, video_data):
        self.current_video = video_data
        url = video_data.get('url')
        theme = theme_mgr.current_theme
        
        # Highlight active card
        for k, v in self.cards.items():
            if k == url:
                v["border"].configure(bg=theme["border_active"])
            else:
                v["border"].configure(bg=theme["border_bold"])
                
        self.selected_title_var.set(f"[ TARGET: {video_data.get('title', 'Unknown')} ]")
        self.download_btn.config(state="normal")
        self.watch_btn.config(state="normal")
        
        # Fetch available formats in background
        def fetch_formats_worker():
            formats = self.downloader.fetch_formats(url)
            self.root.after(0, lambda: self.update_format_options(formats))
        threading.Thread(target=fetch_formats_worker, daemon=True).start()

    def update_format_options(self, formats):
        self.format_combo['values'] = formats
        if formats:
            self.format_var.set(formats[0])

    def quick_stream(self, video_data):
        self.select_video(video_data)
        self.do_watch()

    # --- Animated Stream Buffering Workflow ---
    def do_watch(self):
        if not self.current_video:
            return
            
        url = self.current_video.get('url')
        self._is_extracting_stream = True
        self._stream_anim_frame = 0
        self.watch_btn.config(text="[ ⏳ BUFFERING... ]", state="disabled")
        self.video_player.start_buffering_animation()
        
        self._animate_stream_loop()
        
        def stream_worker():
            stream_url = get_stream_url(url)
            self.root.after(0, lambda: self.play_stream(stream_url))
            
        threading.Thread(target=stream_worker, daemon=True).start()

    def _animate_stream_loop(self):
        if not self._is_extracting_stream:
            return
        spinners = ["◐", "◓", "◑", "◒"]
        self._stream_anim_frame += 1
        s_char = spinners[self._stream_anim_frame % len(spinners)]
        self.status_var.set(f"[ ⚡ EXTRACTING STREAM DATA {s_char} ]")
        self.root.after(150, self._animate_stream_loop)

    def play_stream(self, stream_url):
        self._is_extracting_stream = False
        self.watch_btn.config(text="[ ⚡ STREAM LIVE ]", state="normal")
        self.video_player.stop_buffering_animation()
        
        if stream_url:
            self.status_var.set("[ STREAMING MEDIA ]")
            self.video_player.load_media(stream_url)
        else:
            self.status_var.set("[ STREAM EXTRACTION FAILED ]")
            Messagebox.show_error("Could not extract playable stream URL.", "Playback Error")

    def do_download(self):
        if not self.current_video:
            return
            
        url = self.current_video.get('url')
        title = self.current_video.get('title', 'video')
        quality = self.format_var.get()
        thumb = self.current_video.get('thumbnail_url')
        
        # Add to history if not present
        existing = next((item for item in self.history if item.get('url') == url), None)
        if not existing:
            hist_item = {
                "title": title,
                "url": url,
                "status": "Downloading",
                "thumbnail_url": thumb,
                "duration": self.current_video.get('duration', '--:--'),
                "uploader": self.current_video.get('uploader', '')
            }
            self.history.insert(0, hist_item)
            save_history(self.history)
        else:
            existing['status'] = 'Downloading'
            save_history(self.history)
            
        self.status_var.set(f"[ DOWNLOAD QUEUED: {quality} ]")
        self.downloader.start_download(url, quality, title)
        
        # Switch to Queue tab to observe
        self.switch_tab("history")

    def render_history_cards(self):
        for widget in self.feed_scrollable_frame.winfo_children():
            widget.destroy()
        self.cards.clear()
        
        if not self.history:
            empty_lbl = tk.Label(
                self.feed_scrollable_frame,
                text="[ DOWNLOAD QUEUE IS EMPTY ]",
                font=theme_mgr.get_font("mono_bold"),
                fg=theme_mgr.get("text_muted"),
                bg=theme_mgr.get("bg_canvas"),
                pady=40
            )
            empty_lbl.pack()
            return
            
        for item in self.history:
            self._create_card(item, is_history=True)

    def delete_history_item(self, url):
        self.history = [item for item in self.history if item.get('url') != url]
        save_history(self.history)
        self.render_history_cards()

    def open_download_folder(self):
        folder = self.settings.get('download_folder', '')
        if os.path.exists(folder):
            if os.name == 'nt':
                os.startfile(folder)
            else:
                subprocess.Popen(['xdg-open', folder])

    def on_download_progress(self, url, percent_str, speed_str):
        def update():
            if url in self.cards and "progress" in self.cards[url]:
                card = self.cards[url]
                try:
                    p = float(percent_str.replace('%', ''))
                    card["progress"]['value'] = p
                except ValueError:
                    pass
                if "speed_lbl" in card:
                    card["speed_lbl"].config(text=f"[ {percent_str} // {speed_str} ]")
        self.root.after(0, update)

    def on_download_finished(self, url):
        def update():
            self.status_var.set("[ DOWNLOAD COMPLETED ]")
            for item in self.history:
                if item.get('url') == url:
                    item['status'] = 'Completed'
                    break
            save_history(self.history)
            if self.current_tab == "history":
                self.render_history_cards()
        self.root.after(0, update)

    def on_download_error(self, url, error_msg):
        def update():
            self.status_var.set(f"[ ERROR: {error_msg} ]")
            for item in self.history:
                if item.get('url') == url:
                    item['status'] = 'Failed'
                    break
            save_history(self.history)
            if self.current_tab == "history":
                self.render_history_cards()
        self.root.after(0, update)
