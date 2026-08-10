# YouTube Video Downloader V2

A modern, desktop-native YouTube video downloader and player built in Python. This application features a beautiful dark-mode interface, embedded VLC media playback, multi-threaded downloading, and advanced bot-protection bypassing.

## ✨ Features

- **Modern UI**: Built with `ttkbootstrap` using the sleek "Darkly" theme for a native, clean aesthetic.
- **Search & Play**: Type a search query or paste a direct YouTube URL. The app automatically fetches thumbnails, video length, and titles.
- **Embedded VLC Player**: Stream videos directly inside the app before downloading.
  - Features volume control, interactive seek bar, and time displays.
  - **Theater Mode (Fullscreen)**: Press `F` to seamlessly expand the video across your entire application window without stuttering. Press `Space` to play/pause.
- **Multi-Threaded Download Manager**: Download videos in the background while continuing to search or watch other streams.
- **Download Controls**: True thread-level pausing! You can pause, resume, cancel, or delete downloads on the fly.
- **Bot Protection Bypass**: Integrated `yt-dlp` fallback strategies (using `player_client: all`) to automatically bypass YouTube's recent bot-detection and DPAPI cookie encryption blocks.
- **Persistent History**: Your download history and settings (like download location) are automatically saved and restored across sessions.

## 🚀 Prerequisites

Ensure you have the following installed on your system:
1. **Python 3.8+**
2. **VLC Media Player**: Required for the embedded `python-vlc` player to function. Ensure you download the version of VLC that matches your Python architecture (64-bit VLC for 64-bit Python).

## 📦 Installation

1. Clone or download this repository.
2. Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

*The `requirements.txt` should include:*
- `yt-dlp`
- `ttkbootstrap`
- `python-vlc`
- `Pillow`
- `requests`

## 🎮 Usage

Launch the application by running the main script:

```bash
python main.py
```

### Shortcuts
- `Space`: Play / Pause the current video.
- `F`: Toggle Theater Mode (Fullscreen within the app window).
- `Escape`: Exit Theater Mode.

## 📂 Project Structure

```
Youtube-Video-Downloader/
│
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
│
├── core/
│   ├── downloader.py       # Multi-threaded download manager and yt-dlp logic
│   └── search.py           # YouTube search, URL resolution, and thumbnail fetching
│
└── ui/
    ├── main_window.py      # Core layout, state management, and history panels
    └── video_player.py     # python-vlc wrapper and playback UI controls
```

## 🛠️ Troubleshooting

- **Black Screen during Playback**: Ensure VLC Media Player is correctly installed on your system. If on Linux, ensure `libvlc` is available in your package manager.
- **DPAPI / Bot Detection Errors**: The app handles this automatically via `yt-dlp` client spoofing. If you still encounter issues, ensure you are running the latest version of `yt-dlp` (`pip install --upgrade yt-dlp`).
