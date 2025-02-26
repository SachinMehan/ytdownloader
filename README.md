# YouTube Video Downloader

A simple and user-friendly YouTube Video Downloader with a graphical interface using Tkinter. This tool allows users to download YouTube videos in various formats, including audio-only.

## Features
- **Graphical User Interface (GUI)** built with Tkinter.
- **Supports video and audio downloads** (MP4, MP3, and more).
- **Fetches video information** including title, thumbnail, and description.
- **Allows format selection** before downloading.
- **Customizable download location.**
- **Uses `yt-dlp` for reliable YouTube downloads.**

## Installation
Ensure you have Python installed, then install the required dependencies:
```sh
pip install yt-dlp pillow requests
```

## Usage
Run the script with:
```sh
python ytdownloader.py
```
1. Enter a YouTube video URL.
2. Click "Load Info" to fetch details.
3. Choose the format (video/audio).
4. Select the download folder.
5. Click "Download" and wait for completion.

## Requirements
- Python 3.x
- `yt-dlp`
- `pillow`
- `requests`
- `tkinter` (included with Python standard library)

## License
This project is licensed under the MIT License.
