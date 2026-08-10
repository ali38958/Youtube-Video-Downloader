import yt_dlp
import requests
import os
import hashlib

THUMBNAILS_DIR = "temp_thumbs"

def download_thumbnail(url):
    if not url: return None
    if not os.path.exists(THUMBNAILS_DIR):
        os.makedirs(THUMBNAILS_DIR)
    
    filename = hashlib.md5(url.encode()).hexdigest() + ".jpg"
    filepath = os.path.join(THUMBNAILS_DIR, filename)
    
    if os.path.exists(filepath):
        return filepath
        
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(r.content)
            return filepath
    except Exception:
        pass
    return None

def search_youtube(query, max_results=15):
    ydl_opts = {
        'extract_flat': 'in_playlist',
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {'youtube': {'player_client': ['all']}}
    }
    
    if query.startswith('http://') or query.startswith('https://'):
        search_query = query
    else:
        search_query = f"ytsearch{max_results}:{query}"
        
    results = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            
            if 'entries' in info:
                for entry in info['entries']:
                    if entry:
                        results.append(parse_entry(entry))
            else:
                results.append(parse_entry(info))
    except Exception as e:
        print(f"Error searching youtube: {e}")
        
    return results

def get_stream_url(url):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {'youtube': {'player_client': ['all']}}
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get('url')
    except Exception as e:
        print(f"Error extracting stream: {e}")
        return None

def parse_entry(entry):
    duration = entry.get('duration')
    duration_str = "Unknown"
    if duration:
        try:
            m, s = divmod(int(duration), 60)
            h, m = divmod(m, 60)
            if h > 0:
                duration_str = f"{h}:{m:02d}:{s:02d}"
            else:
                duration_str = f"{m}:{s:02d}"
        except (ValueError, TypeError):
            pass
            
    thumbnails = entry.get('thumbnails', [])
    thumb_url = None
    if thumbnails:
        thumb_url = thumbnails[-1].get('url')
        if thumb_url and thumb_url.startswith('//'):
            thumb_url = 'https:' + thumb_url
            
    return {
        'id': entry.get('id'),
        'title': entry.get('title', 'Unknown Title'),
        'uploader': entry.get('uploader', 'Unknown Channel'),
        'duration': duration_str,
        'thumbnail_url': thumb_url,
        'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
    }
