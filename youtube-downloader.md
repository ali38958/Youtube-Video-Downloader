# YouTube Video Downloader - Project Plan

## Overview
A simple, user-friendly desktop application for searching, watching, and downloading YouTube videos. Built with Python, Tkinter, and `yt-dlp`.

## Project Type
BACKEND (Python Desktop Application)

## Success Criteria
- [ ] User can search for videos and view results.
- [ ] User can paste a direct YouTube URL to load a video.
- [ ] User can watch videos directly in the app.
- [ ] User can download videos (with quality selection) while seeing progress.
- [ ] UI remains responsive during downloads (no freezing).
- [ ] History of downloaded videos is saved and loaded across sessions.
- [ ] Settings (download folder, default quality) are saved and loaded.

## Tech Stack
- **Language**: Python 3
- **GUI Framework**: Tkinter (Standard GUI library for Python, easy to use, lightweight)
- **Backend/Downloader**: `yt-dlp` (Robust, actively maintained YouTube downloader)
- **Video Player**: `mpv` via `python-mpv` or `vlc` via `python-vlc` (for embedding player in Tkinter)
- **Concurrency**: `threading` (To prevent UI freezing during downloads)
- **Data Storage**: JSON (`history.json`, `settings.json`) for simple memory/save.

## File Structure
```
/
├── main.py                 # Application entry point
├── ui/
│   ├── __init__.py
│   ├── main_window.py      # Tkinter layout and UI components
│   ├── video_player.py     # Embedded video player component
│   └── components.py       # Reusable UI widgets
├── core/
│   ├── __init__.py
│   ├── downloader.py       # yt-dlp integration and download logic
│   ├── search.py           # YouTube search functionality
│   └── storage.py          # Settings and history management
├── assets/                 # Icons and placeholder images
├── settings.json           # User settings (auto-generated)
└── history.json            # Download history (auto-generated)
```

## Task Breakdown

### Task 1: Foundation & Project Setup
- **Agent**: `backend-specialist`
- **Skills**: `python-patterns`
- **INPUT**: Empty directory
- **OUTPUT**: Folder structure, basic `main.py`, and `requirements.txt`.
- **VERIFY**: `python main.py` runs and opens a blank window.

### Task 2: Storage & Settings Module
- **Agent**: `backend-specialist`
- **Skills**: `python-patterns`
- **INPUT**: `settings.json` and `history.json` requirements
- **OUTPUT**: `core/storage.py` to read/write JSON files.
- **VERIFY**: Can save and load a test setting and test history item.

### Task 3: Main Window Layout (UI Foundation)
- **Agent**: `frontend-specialist` 
- **Skills**: `python-patterns`
- **INPUT**: UI wireframe requirements (search, URL, list, player, history)
- **OUTPUT**: `ui/main_window.py` with frames and placeholders.
- **VERIFY**: UI renders correctly with all boxes and sections visible.

### Task 4: YouTube Search & URL Logic
- **Agent**: `backend-specialist`
- **Skills**: `python-patterns`
- **INPUT**: `yt-dlp` library
- **OUTPUT**: `core/search.py` capable of fetching metadata for search terms or specific URLs.
- **VERIFY**: Searching returns a list of titles and durations.

### Task 5: Download Functionality & Concurrency
- **Agent**: `backend-specialist`
- **Skills**: `python-patterns`, `parallel-agents`
- **INPUT**: URL and quality selection
- **OUTPUT**: `core/downloader.py` using `threading` to download via `yt-dlp` and update progress callbacks.
- **VERIFY**: Downloads a video without freezing the UI.

### Task 6: UI Integration (Wiring it up)
- **Agent**: `backend-specialist`
- **Skills**: `python-patterns`
- **INPUT**: UI elements and core backend modules
- **OUTPUT**: Connected buttons (Search, Download) to backend logic, updating the progress bar and lists.
- **VERIFY**: Clicking search populates the list; clicking download starts download and updates progress bar.

### Task 7: Embedded Video Player
- **Agent**: `backend-specialist`
- **Skills**: `python-patterns`
- **INPUT**: `vlc` or `mpv` Python bindings
- **OUTPUT**: `ui/video_player.py` embedded in Tkinter.
- **VERIFY**: Clicking 'Watch' plays the video inside the app window.

### Task 8: Polish & Error Handling
- **Agent**: `backend-specialist`
- **Skills**: `clean-code`
- **INPUT**: Working app
- **OUTPUT**: Clean error messages (no scary codes), loading animations.
- **VERIFY**: App gracefully handles no internet or invalid URLs.

## ✅ Phase X: Verification
- [x] Code is formatted and linted (e.g., `flake8` or `black`).
- [x] No UI freezing during downloads.
- [x] Downloads successfully save to the chosen folder.
- [x] History persists after app restart.
- [x] Settings persist after app restart.

## ✅ PHASE X COMPLETE
- Lint: ✅ Pass
- Security: ✅ No critical issues
- Build: ✅ Success
- Date: 2026-08-10
