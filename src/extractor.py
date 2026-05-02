import json
import os
import urllib.parse
from typing import List, Dict, Tuple, Union, Optional

# Determine the project root directory (one level up from 'src')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Absolute path to the raw Spotify data export
INPUT_PATH = os.path.join(BASE_DIR, "data", "Playlist.json")

def extraction_process() -> Tuple[List[Dict[str, any]], List[str]]:
  """
  Parses the Spotify account data JSON to extract track information and playlist names.

  This function handles two distinct data structures found in Spotify exports:
  1. Standard Remote Tracks: Located in the 'track' object.
  2. Local Tracks: Located in the 'localTrack' object with metadata encoded in a URI.

  Returns:
    Tuple containing:
      - List[Dict]: A list of flattened track objects.
      - List[str]: A list of unique playlist names.
  """
  print(f"Searching {INPUT_PATH} for playlist data...")

  if not os.path.exists(INPUT_PATH):
    print(f"Error: Input file not found at {INPUT_PATH}")
    return [], []

  try:
    with open(INPUT_PATH, "r", encoding="utf-8") as file:
      data = json.load(file)
  except json.JSONDecodeError:
    print("Error: Input path is not a valid JSON file or is misformatted.")
    return [], []

  playlists = data.get('playlists')
  if playlists is None:
    print("Error: No 'playlists' key found in the JSON file.")
    return [], []
  
  playlist_names: List[str] = []
  extracted_tracks: List[Dict[str, any]] = []

  for playlist in playlists:
    p_name = playlist.get('name', 'Unknown Playlist')
    playlist_names.append(p_name)

    items = playlist.get('items', [])
    if not items:
      continue

    for item in items:
      # --- SCENARIO A: LOCAL TRACK (Metadata encoded in URI) ---
      # In some exports, local files are stored in a 'localTrack' object.
      # The metadata is usually a colon-separated string in the 'uri' field.
      if 'localTrack' in item and item['localTrack']:
        uri = item['localTrack'].get('uri', '')
        parts = uri.split(':')
        
        # Format: spotify:local:Artist:Album:Title:Duration
        if len(parts) >= 5 and parts[0] == 'spotify' and parts[1] == 'local':
          # unquote_plus handles URL encoding (e.g., '+' or '%20' for spaces)
          artist = urllib.parse.unquote_plus(parts[2])
          title = urllib.parse.unquote_plus(parts[4])
          
          extracted_tracks.append({
            'track_name':    title,
            'artist_name':   artist,
            'playlist_name': p_name,
            'is_local':      True
          })
        continue # Processed as local, skip scenario B

      # --- SCENARIO B: REMOTE TRACK (Standard JSON structure) ---
      if 'track' in item and item['track']:
        track = item['track']
        extracted_tracks.append({
          'track_name':    track.get('trackName', 'Unknown Title'),
          'artist_name':   track.get('artistName', 'Unknown Artist'),
          'playlist_name': p_name,
          'is_local':      False
        })

  print(f"Extraction complete: Found {len(playlist_names)} playlists and {len(extracted_tracks)} total tracks.")
  return extracted_tracks, playlist_names