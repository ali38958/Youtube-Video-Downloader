"""
Brutalism Media Console Theme & Design System
High-contrast, industrial, tactile Neo-Brutalist themes with runtime theme switching.
"""

import tkinter as tk
from tkinter import font as tkfont
import ttkbootstrap as tb
from core.storage import load_settings, save_settings

THEMES = {
    "CYBER_DARK": {
        "id": "CYBER_DARK",
        "name": "CYBER DARK",
        "tb_theme": "darkly",
        "bg_canvas": "#0D0D11",
        "bg_surface": "#16161C",
        "bg_surface_elevated": "#202028",
        "bg_sunken": "#08080A",
        "border_bold": "#2D2D38",
        "border_active": "#FFE600",
        "border_subtle": "#1D1D24",
        "accent_primary": "#FFE600",      # Cyber Yellow
        "accent_secondary": "#00F0FF",    # Cyan
        "accent_success": "#00E676",      # Neon Green
        "accent_danger": "#FF3B30",       # Vivid Red
        "accent_info": "#7B61FF",         # Purple
        "text_primary": "#FFFFFF",
        "text_secondary": "#9E9EA8",
        "text_muted": "#5E5E6C",
        "text_on_accent": "#000000",
        "button_fg": "#000000",
    },
    "RAW_LIGHT": {
        "id": "RAW_LIGHT",
        "name": "RAW LIGHT",
        "tb_theme": "flatly",
        "bg_canvas": "#F4F0EA",
        "bg_surface": "#FFFFFF",
        "bg_surface_elevated": "#E6E1D6",
        "bg_sunken": "#ECE7DC",
        "border_bold": "#000000",
        "border_active": "#FF3300",
        "border_subtle": "#CCCCCC",
        "accent_primary": "#FF3300",      # International Orange
        "accent_secondary": "#0055FF",    # Cobalt
        "accent_success": "#00873E",      # Deep Green
        "accent_danger": "#D32F2F",       # Red
        "accent_info": "#6200EE",         # Violet
        "text_primary": "#000000",
        "text_secondary": "#333333",
        "text_muted": "#777777",
        "text_on_accent": "#FFFFFF",
        "button_fg": "#FFFFFF",
    },
    "ACID_MATRIX": {
        "id": "ACID_MATRIX",
        "name": "ACID MATRIX",
        "tb_theme": "solar",
        "bg_canvas": "#050805",
        "bg_surface": "#0C140C",
        "bg_surface_elevated": "#142214",
        "bg_sunken": "#030603",
        "border_bold": "#1B3B1B",
        "border_active": "#00FF66",
        "border_subtle": "#112411",
        "accent_primary": "#00FF66",      # Acid Green
        "accent_secondary": "#00F0FF",    # Cyan
        "accent_success": "#00FF66",      # Bright Green
        "accent_danger": "#FF0055",       # Acid Magenta
        "accent_info": "#00D4AA",         # Teal
        "text_primary": "#F0FFF0",
        "text_secondary": "#7DB87D",
        "text_muted": "#3D663D",
        "text_on_accent": "#000000",
        "button_fg": "#000000",
    },
    "RETRO_PUNK": {
        "id": "RETRO_PUNK",
        "name": "RETRO PUNK",
        "tb_theme": "superhero",
        "bg_canvas": "#130E1C",
        "bg_surface": "#1F172E",
        "bg_surface_elevated": "#2D2242",
        "bg_sunken": "#0B0811",
        "border_bold": "#453461",
        "border_active": "#FFB800",
        "border_subtle": "#2B1E40",
        "accent_primary": "#FFB800",      # Vivid Gold
        "accent_secondary": "#E056FD",    # Neon Pink/Violet
        "accent_success": "#00E676",      # Green
        "accent_danger": "#FF2A6D",       # Pink Red
        "accent_info": "#7B61FF",         # Violet
        "text_primary": "#FFFFFF",
        "text_secondary": "#B5A7C8",
        "text_muted": "#6E5E85",
        "text_on_accent": "#000000",
        "button_fg": "#000000",
    }
}

class ThemeManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, root=None):
        if getattr(self, "_initialized", False):
            if root and not self.root:
                self.root = root
            return

        self.root = root
        settings = load_settings()
        self.current_theme_id = settings.get("theme", "CYBER_DARK")
        if self.current_theme_id not in THEMES:
            self.current_theme_id = "CYBER_DARK"

        self.listeners = []
        self._initialized = True

    @property
    def current_theme(self):
        return THEMES[self.current_theme_id]

    def get(self, key, default=None):
        return self.current_theme.get(key, default)

    def register_listener(self, callback):
        if callback not in self.listeners:
            self.listeners.append(callback)

    def unregister_listener(self, callback):
        if callback in self.listeners:
            self.listeners.remove(callback)

    def set_theme(self, theme_id):
        if theme_id not in THEMES:
            return
        
        self.current_theme_id = theme_id
        
        # Save to settings
        settings = load_settings()
        settings["theme"] = theme_id
        save_settings(settings)

        # Notify listeners
        for callback in list(self.listeners):
            try:
                callback(self.current_theme)
            except Exception as e:
                print(f"Error updating theme listener: {e}")

    def get_font(self, font_type="body"):
        # Returns standard font tuples for Tkinter
        if font_type == "brand":
            return ("Segoe UI Black", 14, "bold")
        elif font_type == "header":
            return ("Segoe UI", 12, "bold")
        elif font_type == "title":
            return ("Segoe UI", 11, "bold")
        elif font_type == "body":
            return ("Segoe UI", 10, "normal")
        elif font_type == "body_bold":
            return ("Segoe UI", 10, "bold")
        elif font_type == "mono":
            return ("Consolas", 10, "normal")
        elif font_type == "mono_bold":
            return ("Consolas", 10, "bold")
        elif font_type == "mono_sm":
            return ("Consolas", 9, "bold")
        elif font_type == "mono_xs":
            return ("Consolas", 8, "bold")
        elif font_type == "badge":
            return ("Consolas", 9, "bold")
        return ("Segoe UI", 10, "normal")

theme_mgr = ThemeManager()
