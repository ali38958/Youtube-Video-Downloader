
# 🎬 YouTube Video Downloader Pro

A professional desktop application for downloading YouTube videos with advanced features like trim support, format selection, quality options, and theme customization.

## 📋 Table of Contents
- [Features](#features)
- [Application Flow](#application-flow)
- [Technical Architecture](#technical-architecture)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
- [Project Structure](#project-structure)
- [Future Enhancements](#future-enhancements)

## ✨ Features

### Core Features
- **Video Information Fetching** - Automatically retrieves video title, thumbnail, duration, and available formats
- **Format Selection** - Choose from available video/audio formats (MP4, WebM, MKV, MP3)
- **Quality Selection** - Select resolution (144p to 4K/8K where available)
- **Video Trimming** - Download specific portions of videos with visual timeline
- **Custom Save Path** - Set permanent download location (defaults to Downloads folder)
- **Dark/Light Theme** - Toggle between themes with persistent preference
- **Progress Tracking** - Real-time download progress with percentage and speed

### Advanced Features
- **Video Preview** - Play/pause preview of the video before downloading
- **Interactive Timeline** - Drag handles to select start/end points for trimming
- **Batch Downloads** - Support for playlists (future enhancement)
- **Download Queue** - Multiple downloads with priority (future enhancement)

## 🔄 Application Flow

### 1. **Initial State**
```
┌─────────────────────────────────────────────────────────┐
│  [⚙️ Settings]                                    [🌓]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│              YouTube Video Downloader Pro               │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Enter YouTube URL: [________________________]   │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  [🔍 Search & Load Video]                              │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Format: [Disabled Dropdown]                    │   │
│  │  Quality: [Disabled Dropdown]                   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ☐ Trim Video                                          │
│                                                         │
│  [⬇ Download Button - Disabled]                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2. **After Search Button Click**

When user enters a URL and clicks "Search & Load Video":

```
┌─────────────────────────────────────────────────────────┐
│  [⚙️ Settings]                                    [🌓]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│              YouTube Video Downloader Pro               │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Enter YouTube URL: [https://youtube.com/...]    │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  [✓ Video Loaded Successfully]                         │
│  Title: "Amazing Video Title"                          │
│  Duration: 10:25                                       │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Format: [MP4 ▼]      Quality: [1080p ▼]       │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ☑ Trim Video  [Checkbox Checked]                      │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  [▶ Play Preview]                               │   │
│  │                                                  │   │
│  │  ════════════════════════════════════════════   │   │
│  │  ███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   │   │
│  │  └─[Start]────────────────────────────[End]─┘   │   │
│  │  0:00                                    10:25   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  [⬇ Download Video]                                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3. **Detailed Flow Steps**

#### Step 1: Video URL Input
- User pastes YouTube URL into input field
- URL validation (must be valid YouTube URL)
- If invalid, show error message in red

#### Step 2: Search & Load
- User clicks "Search & Load Video" button
- Button shows loading state with spinner
- Application fetches video metadata via yt-dlp/pytube:
  - Video title
  - Available formats (video + audio combinations)
  - Available quality options
  - Video duration
  - Thumbnail URL
- On success:
  - Enable Format & Quality dropdowns
  - Populate dropdowns with available options
  - Enable Trim checkbox
  - Display video title and duration
  - Keep Download button disabled until format/quality selected
- On error:
  - Show error message ("Invalid URL", "Video unavailable", etc.)

#### Step 4: Format & Quality Selection
- User selects desired format:
  - MP4 (most compatible)
  - WebM (smaller size)
  - MKV (high quality)
  - MP3 (audio only)
- User selects quality:
  - Options dynamically populate based on selected format
  - Shows available resolutions (144p, 240p, 360p, 480p, 720p, 1080p, 4K, 8K)
  - "Best" option automatically selects highest available
- Download button becomes enabled

#### Step 5: Trim Video (Optional)
- User checks "Trim Video" checkbox
- Video preview area appears/disappears:
  - **When checked**: Show preview player and timeline
  - **When unchecked**: Hide preview area, download full video
- Preview player features:
  - Paused initially (shows first frame or thumbnail)
  - Play button to preview video content
  - Pause button to stop preview
  - No audio (preview only)
- Timeline features:
  - Visual representation of video duration
  - Two draggable handles:
    - **Left handle (Start time)** - Sets where download begins
    - **Right handle (End time)** - Sets where download ends
  - Real-time display of selected time range
  - Can drag handles independently
  - Minimum trim duration: 3 seconds
  - Shows selected portion highlighted
  - Reset button to clear trim selection

#### Step 6: Download Process
- User clicks "Download Video" button
- Validation checks:
  - Format selected ✓
  - Quality selected ✓
  - If trimmed: Start time < End time ✓
  - Sufficient disk space ✓
- Download starts with progress indicators:
  - Progress bar (0% to 100%)
  - Download speed (MB/s)
  - Time remaining
  - File size
- All UI controls disabled during download
- Cancel button appears (optional)
- On completion:
  - Show success message
  - Open containing folder option
  - Reset UI for next download
- On error:
  - Show error message
  - Re-enable controls

### 4. **Settings Panel**

Located top-right corner (⚙️ gear icon):

**When clicked, opens modal dialog:**

```
┌──────────────────────────────────────────┐
  ⚙️ Settings                        [✕]
├──────────────────────────────────────────┤
│                                          │
│  Download Settings                       │
│  ┌────────────────────────────────────┐ │
│  │ Default Download Path:             │ │
│  │ [C:\Users\Name\Downloads______]    │ │
│  │ [📁 Browse] [💾 Save]              │ │
│  └────────────────────────────────────┘ │
│                                          │
│  Default Format: [MP4 ▼]                │
│  Default Quality: [Best ▼]              │
│                                          │
│  ☐ Auto-open folder after download      │
│  ☐ Show download confirmation           │
│  ☐ Use high-speed downloads             │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │ Theme: [Dark/Light/System]         │ │
│  └────────────────────────────────────┘ │
│                                          │
│  [Cancel]              [Apply & Close]  │
│                                          │
└──────────────────────────────────────────┘
```

**Settings persistence:**
- Save settings to `config.json` in user's app data folder
- Load on application startup
- Settings persist across sessions
- Default path: User's Downloads folder (OS-specific)

### 5. **Theme Switching**

Located next to settings button (🌓 icon):

**Functionality:**
- One-click toggle between Dark and Light mode
- Immediate UI refresh without restart
- Preference saved to settings
- All components update colors dynamically

**Light Theme:** Light backgrounds, dark text
**Dark Theme:** Dark backgrounds, light text, reduced eye strain

## 🏗️ Technical Architecture

### Frontend Components
```
src/
├── app.py                 # Main application controller
├── components/
│   ├── modern_button.py   # Professional button component
│   ├── dropdown.py        # Format & quality selectors
│   ├── input_field.py     # URL input with validation
│   ├── video_preview.py   # Video preview player
│   ├── timeline.py        # Trim timeline with handles
│   ├── settings.py        # Settings dialog
│   └── theme_manager.py   # Dark/light theme handler
└── utils/
    ├── youtube_api.py     # YouTube video fetching
    ├── downloader.py      # Download core logic
    ├── trimmer.py         # Video trimming functionality
    └── config.py          # Settings persistence
```

### Backend Libraries
- **yt-dlp** or **pytube** - YouTube video extraction
- **FFmpeg** - Video trimming and format conversion
- **tkinter** - GUI framework
- **Pillow** - Thumbnail handling
- **requests** - Thumbnail downloading

## 🚀 Installation

### Prerequisites
```bash
Python 3.8+
FFmpeg (for trimming)
Git (optional)
```

### Setup
```bash
# Clone repository
git clone https://github.com/ali38958/Youtube-Video-Downloader.git
cd Youtube-Video-Downloader

# Create virtual environment
python -m venv venv

# Activate venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (required for trimming)
# Windows: Download from https://ffmpeg.org/download.html
# Mac: brew install ffmpeg
# Linux: sudo apt install ffmpeg

# Run application
python src/app.py
```

## 📖 Usage Guide

### Basic Download (No Trim)
1. Launch application
2. Paste YouTube URL
3. Click "Search & Load Video"
4. Select format (MP4 recommended)
5. Select quality (720p/1080p for balance)
6. Click "Download Video"
7. Find file in your Downloads folder

### Trimmed Download
1. Follow steps 1-3 above
2. Check "Trim Video" checkbox
3. Play preview to locate trim points
4. Drag timeline handles to select start/end
5. Verify time range in display
6. Click "Download Video"
7. Trimmed portion saves as new file

### Change Settings
1. Click gear icon (⚙️) top-right
2. Browse to select new download folder
3. Set default format/quality preferences
4. Toggle additional options
5. Click "Apply & Close"

### Switch Theme
1. Click moon/sun icon (🌓) top-right
2. UI instantly changes theme
3. Preference auto-saved

## 📁 Project Structure

```
Youtube-Video-Downloader/
├── src/
│   ├── app.py                 # Main app entry point
│   ├── components/
│   │   ├── __init__.py
│   │   ├── modern_button.py   # Reusable button
│   │   ├── dropdown.py        # Format/quality selects
│   │   ├── input_field.py     # URL input field
│   │   ├── video_preview.py   # Video player
│   │   ├── timeline.py        # Trim timeline widget
│   │   ├── settings.py        # Settings dialog
│   │   └── theme_manager.py   # Theme management
│   └── utils/
│       ├── __init__.py
│       ├── youtube_api.py     # YouTube metadata fetch
│       ├── downloader.py      # Download core logic
│       ├── trimmer.py         # FFmpeg trim wrapper
│       └── config.py          # Config file handler
├── assets/
│   ├── icons/                 # App icons
│   └── styles/                # Theme stylesheets
├── tests/                     # Unit tests
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── .gitignore                # Git ignore rules
└── LICENSE                   # MIT License
```

## 🎯 Future Enhancements

### Phase 2 Features
- [ ] Playlist downloading with batch progress
- [ ] Download queue with priority management
- [ ] Subtitle download (SRT files)
- [ ] Thumbnail preview in video info
- [ ] Drag & drop URL support

### Phase 3 Features
- [ ] Background downloads with system tray
- [ ] Keyboard shortcuts for all actions
- [ ] Export download history
- [ ] Video to GIF conversion tool
- [ ] Audio extraction without re-encoding

### Phase 4 Features
- [ ] Multi-language support (i18n)
- [ ] Plugin system for custom formats
- [ ] Download speed limiting
- [ ] Proxy support
- [ ] Integration with media players

## 🐛 Known Issues
- Very long videos (>2 hours) may have trim performance issues
- Some age-restricted videos require cookies authentication
- 4K/8K downloads require specific formats (WebM/DASH)

## 🤝 Contributing
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License
Distributed under MIT License. See `LICENSE` for more information.

## 📧 Contact
Ali - [@ali38958](https://github.com/ali38958)

Project Link: [https://github.com/ali38958/Youtube-Video-Downloader](https://github.com/ali38958/Youtube-Video-Downloader)

---

**Made with ❤️ using Python & tkinter**
```

This README provides a complete overview of your project's flow and features. It's organized, professional, and gives clear guidance for anyone using or contributing to your YouTube Video Downloader application.