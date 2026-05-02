import sys
from typing import List, Dict, Union
from extractor import extraction_process
from filter import apply_filters, export_queue_to_json
from fetcher import process_queue

def run_pipeline() -> None:
  """
  The main orchestrator for the Spotify Local Cache Salvage (SLCS) pipeline.

  This function handles the end-to-end flow:
  1. Extraction: Pulls track data from the Spotify JSON export.
  2. Interaction: Presents a menu for playlist and track type selection.
  3. Filtering: Refines the track list based on user choices.
  4. Fetching: Downloads the selected tracks via the Fetcher engine.
  """
  print("=== SLCS: Spotify Local Cache Salvage ===\n")

  # PHASE 1: Vacuum the Data
  # The extractor returns both the raw track data and a list of found playlists.
  tracks, available_playlists = extraction_process()
  
  if not tracks:
    print("No tracks found to process. Exiting.")
    return

  # INTERACTIVE MENU: Playlist Selection
  print("\n--- AVAILABLE PLAYLISTS ---")
  for i, p_name in enumerate(available_playlists):
    print(f"[{i + 1}] {p_name}")
  print("[0] ALL Playlists")

  choice = input("\nEnter the numbers of the playlists to fetch (comma separated), or 0 for ALL: ")
  
  target_playlists: Union[str, List[str]] = "all"
  if choice.strip() != "0":
    # Translate numeric menu choices back into the original playlist names
    target_playlists = []
    indices = [int(x.strip()) - 1 for x in choice.split(",") if x.strip().isdigit()]
    for idx in indices:
      if 0 <= idx < len(available_playlists):
        target_playlists.append(available_playlists[idx])

  # INTERACTIVE MENU: Track Type Selection
  print("\n--- TRACK TYPE ---")
  print("[1] Local Files Only (Salvage Mode)")
  print("[2] Remote Files Only")
  print("[3] Both")
  
  type_choice = input("Select track type (1-3): ").strip()
  mode_map = {"1": "local_only", "2": "remote_only", "3": "both"}
  # Default to local_only if input is invalid
  mode = mode_map.get(type_choice, "local_only")

  # PHASE 1.5: Filtering & Queueing
  # Apply the user's filters and prepare the download queue.
  print("\n[Processing Queue...]")
  filtered_queue = apply_filters(tracks, target_playlists=target_playlists, mode=mode)
  
  # Export the queue to JSON so the fetcher can read it from disk
  if export_queue_to_json(filtered_queue):
    # PHASE 2: Download Engine
    # This phase performs the actual YouTube search and MP3 conversion.
    print("\n[Starting Download Engine...]")
    downloaded_files = process_queue()
    
    # Note: Phase 3 (ID3 Tagging) will be integrated here in a future update.
    print(f"\nPipeline execution finished. {len(downloaded_files)} files processed.")
  else:
    print("\nPipeline aborted: Could not generate download queue.")

if __name__ == "__main__":
  try:
    run_pipeline()
  except KeyboardInterrupt:
    print("\n\nProcess interrupted by user. Exiting.")
    sys.exit(0)
  except Exception as e:
    print(f"\n\n[FATAL ERROR] {e}")
    sys.exit(1)
