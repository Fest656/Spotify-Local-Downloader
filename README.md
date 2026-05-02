# 🎵 SLCS: Spotify Local Cache Salvage

A simple Python CLI pipeline designed to extract, filter, and salvage tracks from Spotify account data exports. SLCS specializes in recovering "local files" and standard playlist tracks by fetching high-quality audio from YouTube.
   
---

## 🚀 Key Features

- **Automated Extraction**: Deep-parses Spotify's `Playlist.json` to recover metadata even from obfuscated local file URIs.
- **Intelligent Filtering**: Choose between *Local Files Only*, *Remote Tracks Only*, or *Both*. Select specific playlists to process.
- **Deduplication Engine**: Ensures no redundant downloads within the same playlist folders.
- **Automated Fetching**: Leverages `yt-dlp` to find the best matching audio on YouTube.
- **Smart Organization**: Automatically organizes downloads into folders named after your original Spotify playlists.
- **Rate-Limit Resilient**: Built-in human-like delays to prevent IP flagging during batch downloads.

---

## 🛠️ Technical Stack

- **Language**: Python 3.x
- **Extraction**: `json`, `urllib.parse`
- **Download Engine**: [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- **Audio Processing**: [FFmpeg](https://ffmpeg.org/) (Required for MP3 conversion)

---

## 📦 Prerequisites

Before running the pipeline, ensure you have the following installed:

1. **Python 3.8+**
2. **FFmpeg**: Must be installed and available in your system's `PATH`.
3. **Dependencies**:
   ```bash
   pip install yt-dlp
   ```

---

## 📖 How to Use

1. **Get your Data**: Request your "Account Data" from Spotify. You will eventually receive a JSON file named `Playlist.json`.
2. **Setup**: Place your `Playlist.json` inside the `data/` directory of this project.
3. **Run**:
   ```bash
   python src/main.py
   ```
4. **Follow the Prompts**:
   - Select the playlists you want to download (or 0 for all).
   - Choose the track type (Salvage Mode for local files, Remote Only, or Both).
5. **Collect Downloads**: Your MP3s will be waiting in the `output/` directory, neatly organized by playlist.

---

## 📁 Project Structure

```text
Spotify-Local-Downloader/
├── data/               # Input JSON and generated download queues
├── src/                # Core pipeline logic
│   ├── main.py         # Entry point & orchestrator
│   ├── extractor.py    # Data parsing logic
│   ├── filter.py       # Queue preparation & deduplication
│   └── fetcher.py      # YouTube search & download engine
├── output/             # Downloaded MP3s (organized by playlist)
└── README.md           # You are here!
```

---

## ⚖️ Disclaimer

This tool is for personal use and archival purposes only. Please respect the copyright of the artists and content creators. Use of this tool may be subject to YouTube's and Spotify's Terms of Service.
