import tkinter as tk
import ttkbootstrap as tb
import sys
import threading
import time

try:
    import vlc
except ImportError:
    vlc = None

class VideoPlayer(tb.Frame):
    def __init__(self, parent, fullscreen_callback=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.fullscreen_callback = fullscreen_callback
        self.is_fullscreen = False
        
        self.instance = None
        self.player = None
        self._is_seeking = False
        
        self.configure(takefocus=True)
        
        if vlc is None:
            tb.Label(self, text="VLC is not installed.\nPlease install python-vlc and VLC.", bootstyle="danger").pack(expand=True)
            return
            
        self.instance = vlc.Instance('--no-xlib')
        self.player = self.instance.media_player_new()
        
        self.video_frame = tk.Frame(self, bg="black")
        self.video_frame.pack(fill="both", expand=True)
        self.video_frame.bind("<Button-1>", lambda e: self.focus_set())
        
        self.seek_var = tb.DoubleVar(value=0)
        self.seek_slider = tb.Scale(self, variable=self.seek_var, from_=0, to=100, orient="horizontal")
        self.seek_slider.pack(fill="x", padx=10, pady=5)
        
        self.seek_slider.bind("<ButtonPress-1>", self._on_seek_start)
        self.seek_slider.bind("<ButtonRelease-1>", self._on_seek_end)
        
        self.controls = tb.Frame(self)
        self.controls.pack(fill="x", side="bottom", pady=5)
        self.controls.bind("<Button-1>", lambda e: self.focus_set())
        
        self.play_btn = tb.Button(self.controls, text="Play/Pause", command=self.toggle_play_pause, bootstyle="success")
        self.play_btn.pack(side="left", padx=5)
        
        self.stop_btn = tb.Button(self.controls, text="Stop", command=self.stop, bootstyle="danger")
        self.stop_btn.pack(side="left", padx=5)
        
        tb.Label(self.controls, text="Vol:").pack(side="left", padx=5)
        self.volume_scale = tb.Scale(self.controls, from_=0, to=100, orient="horizontal", command=self.set_volume)
        self.volume_scale.set(50)
        self.volume_scale.pack(side="left", fill="x", expand=True, padx=5)
        
        self.fullscreen_btn = tb.Button(self.controls, text="⛶ Fullscreen", command=self.toggle_fullscreen_ui, bootstyle="secondary")
        self.fullscreen_btn.pack(side="right", padx=5)
        
        self.time_label = tb.Label(self.controls, text="00:00 / 00:00")
        self.time_label.pack(side="right", padx=10)
        
        self.bind("<space>", lambda e: self.toggle_play_pause())
        self.bind("<f>", lambda e: self.toggle_fullscreen_ui())
        self.bind("<F>", lambda e: self.toggle_fullscreen_ui())
        self.bind("<Escape>", lambda e: self.exit_fullscreen())
        
        self._bind_window()
        self._start_update_loop()

    def _bind_window(self, handle=None):
        if handle is None:
            handle = self.video_frame.winfo_id()
        if sys.platform.startswith('linux'):
            self.player.set_xwindow(handle)
        elif sys.platform == "win32":
            self.player.set_hwnd(handle)
        elif sys.platform == "darwin":
            self.player.set_nsobject(handle)

    def _on_seek_start(self, event):
        self._is_seeking = True

    def _on_seek_end(self, event):
        if self.player:
            pos = self.seek_var.get() / 100.0
            self.player.set_position(pos)
        self._is_seeking = False

    def _start_update_loop(self):
        def update():
            if self.player and not self._is_seeking:
                pos = self.player.get_position()
                if pos >= 0:
                    self.seek_var.set(pos * 100)
                    
                time_ms = self.player.get_time()
                length_ms = self.player.get_length()
                
                if time_ms >= 0 and length_ms > 0:
                    t_s = time_ms // 1000
                    l_s = length_ms // 1000
                    self.time_label.config(text=f"{t_s//60:02d}:{t_s%60:02d} / {l_s//60:02d}:{l_s%60:02d}")
                    
            self.after(500, update)
        self.after(500, update)

    def load_media(self, url):
        if not self.instance:
            return
            
        media = self.instance.media_new(url)
        self.player.set_media(media)
        self.play()
        self.volume_scale.set(50)
        self.player.audio_set_volume(50)
        self.focus_set()

    def play(self):
        if self.player:
            self.player.play()

    def pause(self):
        if self.player:
            self.player.pause()
            
    def toggle_play_pause(self):
        if self.player:
            state = self.player.get_state()
            if state == vlc.State.Playing:
                self.player.pause()
            else:
                self.player.play()
                
    def toggle_fullscreen_ui(self):
        if self.fullscreen_callback:
            self.is_fullscreen = not self.is_fullscreen
            self.fullscreen_callback(self.is_fullscreen)
            
    def exit_fullscreen(self):
        if self.is_fullscreen:
            self.toggle_fullscreen_ui()
            
    def stop(self):
        if self.player:
            self.player.stop()

    def set_volume(self, val):
        if self.player:
            self.player.audio_set_volume(int(float(val)))
