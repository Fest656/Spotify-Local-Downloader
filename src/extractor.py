import json
import os

INPUT_PATH = "data/.../"

def extraction_process():
  print(f"Searching {INPUT_PATH} for playlist data...")
  if (not os.path.exists(INPUT_PATH)):
    print("Error: Input path does not exist.")
    return False
  try:
    with open(INPUT_PATH, "r", encoding="utf-8") as file:
      data = json.load(file)
  except json.JSONDecodeError:
    print("Error: Input path is not a valid JSON file or JSON file is misformatted.")
    return False

  playlists = data.get('playlists')
  if playlists is None:
    print("Error: No playlists found in the JSON file.")
    return False
  
  playlist_list = []
  track_list = []

  for playlist in playlists:

    items = playlist.get('items')
    if items is None:
      print("Error: No items found in the playlist.")
      continue

    playlist_list.append(playlist.get('name'))

    for item in items:
      track = item.get('track')
      if track is None:
        print("Error: No track found in the item.")
        continue

      # We can skip the fail safe checks for this as a valid track has these fields
      track_data = {
        'track_name':     track.get('name'),
        'artist_name':    track.get('artists'),
        'playlist_name':  playlist.get('name'),
        'is_local':       track.get('localTrack', False) is True
      }

      track_list.append(track_data)

  print(f"Found {len(playlist_list)} playlists and {len(track_list)} total tracks.")
  
  return track_list, playlist_list
