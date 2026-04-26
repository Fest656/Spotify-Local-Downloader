import os
import json

OUTPUT_PATH = "data/download_queue.json"

def apply_filters(track_list, target_playlists="all", mode="local_only"):
  print(f"Applying filters... Playlists: {target_playlists} | Mode: {mode}")
  
  # Deduplication per playlist to allow same song in different folders
  unique_tracker = set()
  filtered_queue = []

  for track in track_list:
    p_name = track['playlist_name']
    
    # 1. Playlist Filter
    if target_playlists != "all":
      if p_name not in target_playlists:
        continue

    # 2. Local/Remote Filter
    is_local = track['is_local']
    if mode == "local_only" and not is_local:
      continue
    if mode == "remote_only" and is_local:
      continue

    # 3. Deduplication Check
    artist = track['artist_name']
    title = track['track_name']
    
    signature = (p_name, artist, title)
    
    if signature not in unique_tracker:
      unique_tracker.add(signature)
      filtered_queue.append(track)

  print(f"Filtering complete. {len(filtered_queue)} tracks queued.")
  return filtered_queue

def export_queue_to_json(filtered_queue):
  if not filtered_queue:
    print("Queue is empty. No files matched your filters.")
    return False

  # Ensure the target directory exists
  os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

  with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
    json.dump(filtered_queue, file, indent=2)
      
  print(f"Success: Wrote download queue to {OUTPUT_PATH}")
  return True