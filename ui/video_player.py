import tkinter as tk
import ttkbootstrap as tb
import sys
import threading
import time
from ui.theme import theme_mgr

try:
    import vlc
except ImportError:
    vlc = None

class VideoPlayer(tk.Frame):
    def __init__(self, parent, fullscreen_callback=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.fullscreen_callback = fullscreen_callback
        self.is_fullscreen = False
        
        self.instance = None
        self.player = None
        self._is_seeking = False
        self._is_buffering = False
        self._buffering_frame = 0
        
        self.configure(takefocus=True)
        
        if vlc is None:
            self.error_label = tk.Label(
                self, 
                text="[ VLC ENGINE MISSING ]\nPlease install python-vlc and 64-bit VLC media player.",
                font=theme_mgr.get_font("mono_bold"),
                fg=theme_mgr.get("accent_danger"),
                bg=theme_mgr.get("bg_surface")
            )
            self.error_label.pack(expand=True, fill="both", padx=20, pady=20)
            return
            
        # VLC Configuration flags to prevent D3D11VA hardware decode buffer crashes on seek
        vlc_args = [
            '--no-xlib',
            '--avcodec-hw=none',          # Software decoding for zero-crash seek stability
            '--network-caching=2500',     # 2.5s network buffer to ensure smooth seeking
            '--file-caching=2000',
            '--live-caching=2000',
            '--clock-jitter=0',
            '--drop-late-frames',
            '--skip-frames',
            '--quiet'
        ]
        self.instance = vlc.Instance(vlc_args)
        self.player = self.instance.media_player_new()
        
        # Player Viewport Bezel
        self.viewport_container = tk.Frame(
            self,
            bg=theme_mgr.get("border_bold"),
            padx=2,
            pady=2
        )
        self.viewport_container.pack(fill="both", expand=True)

        self.video_frame = tk.Frame(self.viewport_container, bg="#000000")
        self.video_frame.pack(fill="both", expand=True)
        self.video_frame.bind("<Button-1>", lambda e: self.focus_set())
        self.video_frame.bind("<Double-Button-1>", lambda e: self.toggle_fullscreen_ui())
        
        # Seek Bar Area
        self.seek_container = tk.Frame(self, bg=theme_mgr.get("bg_surface"), pady=4)
        self.seek_container.pack(fill="x")
        
        self.seek_var = tk.DoubleVar(value=0)
        self.seek_slider = tb.Scale(
            self.seek_container, 
            variable=self.seek_var, 
            from_=0, 
            to=100, 
            orient="horizontal",
            bootstyle="warning"
        )
        self.seek_slider.pack(fill="x", padx=10)
        
        # Pixel-perfect scrubbing bindings
        self.seek_slider.bind("<ButtonPress-1>", self._on_seek_start)
        self.seek_slider.bind("<B1-Motion>", self._on_seek_motion)
        self.seek_slider.bind("<ButtonRelease-1>", self._on_seek_end)
        
        # Brutalist Controls Bar
        self.controls = tk.Frame(self, bg=theme_mgr.get("bg_surface"), padx=8, pady=6)
        self.controls.pack(fill="x", side="bottom")
        self.controls.bind("<Button-1>", lambda e: self.focus_set())
        
        # Play / Pause Tactical Button
        self.play_btn = tk.Button(
            self.controls,
            text="▶ PLAY",
            font=theme_mgr.get_font("mono_bold"),
            bg=theme_mgr.get("accent_primary"),
            fg=theme_mgr.get("text_on_accent"),
            activebackground=theme_mgr.get("accent_secondary"),
            activeforeground="#000000",
            relief="solid",
            bd=2,
            cursor="hand2",
            padx=12,
            pady=3,
            command=self.toggle_play_pause
        )
        self.play_btn.pack(side="left", padx=4)
        
        # Stop Tactical Button
        self.stop_btn = tk.Button(
            self.controls,
            text="⏹ STOP",
            font=theme_mgr.get_font("mono_bold"),
            bg=theme_mgr.get("bg_surface_elevated"),
            fg=theme_mgr.get("text_primary"),
            activebackground=theme_mgr.get("accent_danger"),
            activeforeground="#FFFFFF",
            relief="solid",
            bd=2,
            cursor="hand2",
            padx=10,
            pady=3,
            command=self.stop
        )
        self.stop_btn.pack(side="left", padx=4)
        
        # Volume readout & slider
        self.vol_label = tk.Label(
            self.controls, 
            text="VOL:", 
            font=theme_mgr.get_font("mono_bold"),
            fg=theme_mgr.get("text_secondary"),
            bg=theme_mgr.get("bg_surface")
        )
        self.vol_label.pack(side="left", padx=(12, 4))
        
        self.volume_scale = tb.Scale(
            self.controls, 
            from_=0, 
            to=100, 
            orient="horizontal", 
            command=self.set_volume,
            bootstyle="info"
        )
        self.volume_scale.set(65)
        self.volume_scale.pack(side="left", fill="x", expand=True, padx=4)
        
        # Fullscreen Toggle Button
        self.fullscreen_btn = tk.Button(
            self.controls,
            text="⛶ FULLSCREEN",
            font=theme_mgr.get_font("mono_bold"),
            bg=theme_mgr.get("bg_surface_elevated"),
            fg=theme_mgr.get("text_primary"),
            activebackground=theme_mgr.get("accent_primary"),
            activeforeground=theme_mgr.get("text_on_accent"),
            relief="solid",
            bd=2,
            cursor="hand2",
            padx=8,
            pady=3,
            command=self.toggle_fullscreen_ui
        )
        self.fullscreen_btn.pack(side="right", padx=4)
        
        # Timecode Monospace Badge
        self.time_label = tk.Label(
            self.controls,
            text="[ 00:00 // 00:00 ]",
            font=theme_mgr.get_font("mono_bold"),
            bg=theme_mgr.get("bg_sunken"),
            fg=theme_mgr.get("accent_secondary"),
            relief="solid",
            bd=1,
            padx=8,
            pady=3
        )
        self.time_label.pack(side="right", padx=6)
        
        # Keyboard shortcuts
        self.bind("<space>", lambda e: self.toggle_play_pause())
        self.bind("<f>", lambda e: self.toggle_fullscreen_ui())
        self.bind("<F>", lambda e: self.toggle_fullscreen_ui())
        self.bind("<Escape>", lambda e: self.exit_fullscreen())
        self.bind("<Left>", lambda e: self.seek_relative(-5000))
        self.bind("<Right>", lambda e: self.seek_relative(5000))
        self.bind("<j>", lambda e: self.seek_relative(-10000))
        self.bind("<l>", lambda e: self.seek_relative(10000))
        
        # Register theme changes
        theme_mgr.register_listener(self.apply_theme)
        
        self._bind_window()
        self._start_update_loop()

    def apply_theme(self, theme):
        try:
            self.configure(bg=theme["bg_surface"])
            if hasattr(self, "viewport_container"):
                self.viewport_container.configure(bg=theme["border_bold"])
            if hasattr(self, "seek_container"):
                self.seek_container.configure(bg=theme["bg_surface"])
            if hasattr(self, "controls"):
                self.controls.configure(bg=theme["bg_surface"])
            if hasattr(self, "vol_label"):
                self.vol_label.configure(bg=theme["bg_surface"], fg=theme["text_secondary"])
            if hasattr(self, "play_btn"):
                self.play_btn.configure(
                    bg=theme["accent_primary"],
                    fg=theme["text_on_accent"],
                    activebackground=theme["accent_secondary"]
                )
            if hasattr(self, "stop_btn"):
                self.stop_btn.configure(
                    bg=theme["bg_surface_elevated"],
                    fg=theme["text_primary"],
                    activebackground=theme["accent_danger"]
                )
            if hasattr(self, "fullscreen_btn"):
                self.fullscreen_btn.configure(
                    bg=theme["bg_surface_elevated"],
                    fg=theme["text_primary"],
                    activebackground=theme["accent_primary"],
                    activeforeground=theme["text_on_accent"]
                )
            if hasattr(self, "time_label"):
                self.time_label.configure(
                    bg=theme["bg_sunken"],
                    fg=theme["accent_secondary"]
                )
        except Exception as e:
            print(f"Error applying theme in VideoPlayer: {e}")

    def _bind_window(self, handle=None):
        if handle is None:
            handle = self.video_frame.winfo_id()
        if sys.platform.startswith('linux'):
            self.player.set_xwindow(handle)
        elif sys.platform == "win32":
            self.player.set_hwnd(handle)
        elif sys.platform == "darwin":
            self.player.set_nsobject(handle)

    def _get_seek_pct_from_event(self, event):
        width = self.seek_slider.winfo_width()
        if width <= 0:
            return 0.0
        # ttk scale track padding offset
        pad = 8
        usable = max(1, width - (2 * pad))
        rel_x = max(0, min(usable, event.x - pad))
        return (rel_x / usable) * 100.0

    def _on_seek_start(self, event):
        self._is_seeking = True
        target_pct = self._get_seek_pct_from_event(event)
        self.seek_var.set(target_pct)
        self._update_time_preview(target_pct)
        self._perform_seek_to_pct(target_pct)

    def _on_seek_motion(self, event):
        self._is_seeking = True
        target_pct = self._get_seek_pct_from_event(event)
        self.seek_var.set(target_pct)
        self._update_time_preview(target_pct)

    def _on_seek_end(self, event):
        target_pct = self._get_seek_pct_from_event(event)
        self.seek_var.set(target_pct)
        self._perform_seek_to_pct(target_pct)
        self.after(350, self._finish_seeking)

    def _update_time_preview(self, pct):
        if self.player:
            length_ms = self.player.get_length()
            if length_ms > 0:
                cur_s = int((pct / 100.0) * (length_ms // 1000))
                tot_s = length_ms // 1000
                self.time_label.config(text=f"[ {cur_s//60:02d}:{cur_s%60:02d} // {tot_s//60:02d}:{tot_s%60:02d} ]")

    def _perform_seek_to_pct(self, target_pct):
        if self.player:
            try:
                length_ms = self.player.get_length()
                if length_ms > 0:
                    target_time_ms = int((target_pct / 100.0) * length_ms)
                    self.player.set_time(target_time_ms)
                else:
                    self.player.set_position(target_pct / 100.0)
            except Exception as e:
                print(f"Seek error: {e}")

    def _finish_seeking(self):
        self._is_seeking = False

    def seek_relative(self, delta_ms):
        if self.player:
            try:
                cur_time = self.player.get_time()
                length_ms = self.player.get_length()
                if cur_time >= 0:
                    new_time = max(0, cur_time + delta_ms)
                    if length_ms > 0:
                        new_time = min(length_ms, new_time)
                        self.seek_var.set((new_time / length_ms) * 100.0)
                    self.player.set_time(new_time)
            except Exception as e:
                print(f"Relative seek error: {e}")

    def start_buffering_animation(self):
        self._is_buffering = True
        self._animate_buffering()

    def stop_buffering_animation(self):
        self._is_buffering = False

    def _animate_buffering(self):
        if not self._is_buffering:
            return
        patterns = [
            "[ ⏳ BUFFERING ░▒▓█ ]",
            "[ ⏳ BUFFERING █░▒▓ ]",
            "[ ⏳ BUFFERING ▓█░▒ ]",
            "[ ⏳ BUFFERING ▒▓█░ ]"
        ]
        self._buffering_frame = (self._buffering_frame + 1) % len(patterns)
        self.time_label.config(text=patterns[self._buffering_frame])
        self.after(200, self._animate_buffering)

    def _start_update_loop(self):
        def update():
            if self.player and not self._is_seeking and not self._is_buffering:
                try:
                    pos = self.player.get_position()
                    if pos >= 0:
                        self.seek_var.set(pos * 100)
                        
                    time_ms = self.player.get_time()
                    length_ms = self.player.get_length()
                    
                    if time_ms >= 0 and length_ms > 0:
                        t_s = time_ms // 1000
                        l_s = length_ms // 1000
                        self.time_label.config(text=f"[ {t_s//60:02d}:{t_s%60:02d} // {l_s//60:02d}:{l_s%60:02d} ]")
                    
                    state = self.player.get_state()
                    if state == vlc.State.Playing:
                        self.play_btn.config(text="⏸ PAUSE")
                    else:
                        self.play_btn.config(text="▶ PLAY")
                except Exception:
                    pass
                    
            self.after(500, update)
        self.after(500, update)

    def load_media(self, url):
        if not self.instance:
            return
            
        media = self.instance.media_new(url)
        self.player.set_media(media)
        self.play()
        self.volume_scale.set(65)
        self.player.audio_set_volume(65)
        self.focus_set()

    def play(self):
        if self.player:
            self.player.play()
            self.play_btn.config(text="⏸ PAUSE")

    def pause(self):
        if self.player:
            self.player.pause()
            self.play_btn.config(text="▶ PLAY")
            
    def toggle_play_pause(self):
        if self.player:
            state = self.player.get_state()
            if state == vlc.State.Playing:
                self.player.pause()
                self.play_btn.config(text="▶ PLAY")
            else:
                self.player.play()
                self.play_btn.config(text="⏸ PAUSE")
                
    def toggle_fullscreen_ui(self):
        if self.fullscreen_callback:
            self.is_fullscreen = not self.is_fullscreen
            self.fullscreen_btn.config(text="[ ✕ EXIT FULLSCREEN ]" if self.is_fullscreen else "[ ⛶ FULLSCREEN ]")
            self.fullscreen_callback(self.is_fullscreen)
            
    def exit_fullscreen(self):
        if self.is_fullscreen:
            self.toggle_fullscreen_ui()
            
    def stop(self):
        if self.player:
            self.player.stop()
            self.play_btn.config(text="▶ PLAY")
            self.time_label.config(text="[ 00:00 // 00:00 ]")
            self.seek_var.set(0)

    def set_volume(self, val):
        if self.player:
            self.player.audio_set_volume(int(float(val)))
