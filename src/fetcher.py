import json
import os
import time
import yt_dlp
from typing import List, Dict, Optional, Any

# Determine the project root directory (one level up from 'src')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Absolute path to the download queue
QUEUE_PATH = os.path.join(BASE_DIR, "data", "download_queue.json")
# Absolute path to the output directory
OUTPUT_BASE_DIR = os.path.join(BASE_DIR, "output")

def download_track(track_data: Dict[str, Any]) -> Optional[str]:
  """
  Searches YouTube for a single track, downloads it, and converts it to MP3.

  This function uses yt-dlp to interface with YouTube. It constructs a search query
  based on the artist and title, then applies a series of post-processors to
  ensure the output is a high-quality MP3 file.

  Args:
    track_data: Dictionary containing 'artist_name', 'track_name', and 'playlist_name'.

  Returns:
    Optional[str]: The absolute file path to the downloaded MP3, or None if failed.
  """
  artist = track_data.get('artist_name', 'Unknown Artist')
  title = track_data.get('track_name', 'Unknown Title')
  playlist = track_data.get('playlist_name', 'Uncategorized')
  
  # ytsearch1: tells yt-dlp to take the very first result from a YouTube search
  search_query = f"ytsearch1:{artist} - {title}"
  
  # Target directory: output/[Playlist Name]/
  playlist_dir = os.path.join(OUTPUT_BASE_DIR, playlist)
  # Template for filename: Artist - Title.mp3 (yt-dlp handles the extension via postprocessors)
  output_template = os.path.join(playlist_dir, f"{artist} - {title}.%(ext)s")

  # yt-dlp configuration: This is the core engine setup.
  # We specify how to find, download, and transform the stream.
  ydl_opts = {
    # 'bestaudio/best' ensures we get the highest quality audio stream available
    'format': 'bestaudio/best',
    # 'outtmpl' defines the filesystem path and naming convention
    'outtmpl': output_template,
    # 'noplaylist' ensures if a search result is a YT playlist, we only grab the first video
    'noplaylist': True,
    # 'quiet' suppresses most terminal output except errors/important info
    'quiet': False,
    'no_warnings': True,
    # Postprocessors allow us to run ffmpeg after the download finishes
    'postprocessors': [{
      'key': 'FFmpegExtractAudio',
      'preferredcodec': 'mp3',
      # '0' indicates the best possible variable bitrate (VBR) for MP3
      'preferredquality': '0',
    }],
  }

  print(f"\n[FETCHING] {artist} - {title} (Playlist: {playlist})")
  
  try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      # ydl.download() performs the actual network request and file writing
      error_code = ydl.download([search_query])
      
      if error_code == 0:
        # Success: Return the path to the final .mp3 file
        expected_path = os.path.join(playlist_dir, f"{artist} - {title}.mp3")
        return expected_path
      else:
        print(f"[ERROR] yt-dlp returned error code {error_code} for {title}")
        return None
        
  except Exception as e:
    print(f"[CRASH] Failed to download {title}. Reason: {e}")
    return None

def process_queue() -> List[str]:
  """
  Iterates through the download queue and manages the overall download process.

  This function handles the logic of reading the queue file, triggering individual
  downloads, and implementing rate limiting to avoid being flagged by YouTube.

  Returns:
    List[str]: A list of file paths for all tracks successfully downloaded in this session.
  """
  if not os.path.exists(QUEUE_PATH):
    print(f"Error: Queue file not found at {QUEUE_PATH}")
    return []

  try:
    with open(QUEUE_PATH, "r", encoding="utf-8") as file:
      queue = json.load(file)
  except Exception as e:
    print(f"Error: Could not read queue file. Reason: {e}")
    return []

  if not queue:
    print("Queue is empty. Nothing to download.")
    return []

  print(f"Starting engine: {len(queue)} tracks in queue.")
  
  successful_downloads: List[str] = []

  for index, track in enumerate(queue):
    file_path = download_track(track)
    
    if file_path and os.path.exists(file_path):
      successful_downloads.append(file_path)
    
    # Rate Limiting: Pausing between downloads mimics human behavior and
    # prevents IP-based rate limiting from YouTube.
    if index < len(queue) - 1:
      print("[WAITING] Pausing for 3 seconds to respect rate limits...")
      time.sleep(3)

  print(f"\n--- FETCH COMPLETE ---")
  print(f"Successfully downloaded {len(successful_downloads)}/{len(queue)} tracks.")
  return successful_downloads

if __name__ == "__main__":
  # Standalone execution for testing the fetcher logic
  process_queue()
