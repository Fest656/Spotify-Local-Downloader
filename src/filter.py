import os
import json
from typing import List, Dict, Union, Set, Tuple

# Determine the project root directory (one level up from 'src')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The absolute path where the filtered download list is stored
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "download_queue.json")

def apply_filters(
  track_list: List[Dict[str, any]], 
  target_playlists: Union[str, List[str]] = "all", 
  mode: str = "local_only"
) -> List[Dict[str, any]]:
  """
  Filters the extracted tracks based on playlist selection and file type (local/remote).

  This step ensures we only download exactly what the user wants and removes duplicates 
  within the same playlist folder.

  Args:
    track_list: The raw list of extracted tracks from extractor.py.
    target_playlists: Either the string "all" or a list of specific playlist names.
    mode: Filter mode - "local_only", "remote_only", or "both".

  Returns:
    List[Dict]: A refined list of tracks ready for the download engine.
  """
  print(f"Applying filters... Playlists: {target_playlists} | Mode: {mode}")
  
  # The unique_tracker set prevents the same song from being added twice to the SAME playlist.
  # We use a tuple of (playlist_name, artist, title) as the unique signature.
  unique_tracker: Set[Tuple[str, str, str]] = set()
  filtered_queue: List[Dict[str, any]] = []
  skipped_by_mode = 0

  for track in track_list:
    p_name = track['playlist_name']
    
    # 1. Playlist Filter: Check if this track belongs to a selected playlist
    if target_playlists != "all":
      if p_name not in target_playlists:
        continue

    # 2. Local/Remote Filter: Filter based on whether the file is "local" in Spotify
    is_local = track['is_local']
    if mode == "local_only" and not is_local:
      skipped_by_mode += 1
      continue
    if mode == "remote_only" and is_local:
      skipped_by_mode += 1
      continue

    # 3. Deduplication Check
    artist = track['artist_name']
    title = track['track_name']
    
    signature = (p_name, artist, title)
    
    if signature not in unique_tracker:
      unique_tracker.add(signature)
      filtered_queue.append(track)

  if skipped_by_mode > 0:
    print(f"Note: Skipped {skipped_by_mode} tracks because they did not match the '{mode}' mode.")
    if mode == "local_only" and len(filtered_queue) == 0:
      print("Hint: Your Spotify data might not contain any 'local' files. Try selecting 'Both' in the menu.")

  print(f"Filtering complete: {len(filtered_queue)} tracks queued for download.")
  return filtered_queue

def export_queue_to_json(filtered_queue: List[Dict[str, any]]) -> bool:
  """
  Saves the filtered track list to a JSON file for Phase 2 (Fetcher) to consume.

  Args:
    filtered_queue: The list of tracks that passed the filter criteria.

  Returns:
    bool: True if the file was written successfully, False otherwise.
  """
  if not filtered_queue:
    print("Warning: Queue is empty. No tracks matched your filters.")
    return False

  # Ensure the data directory exists before trying to write to it
  os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

  try:
    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
      json.dump(filtered_queue, file, indent=2)
    print(f"Success: Wrote download queue to {OUTPUT_PATH}")
    return True
  except Exception as e:
    print(f"Error: Failed to write queue file. Reason: {e}")
    return False