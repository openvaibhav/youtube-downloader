# YouTube Downloader

A Python application to download YouTube videos or extract audio from videos and playlists. Available in both command-line and GUI versions.

## Features

- Download individual YouTube videos
- Download entire playlists
- Choose between video or audio format
- Select video resolution (2160p, 1440p, 1080p, 720p, 480p, 360p, 240p, 144p)
- Select audio bitrate (320kbps, 256kbps, 192kbps, 128kbps, 96kbps, 64kbps)
- Automatic creation of downloads directory
- Sanitized filenames for compatibility
- Support for high-quality video downloads
- Progress tracking for downloads
- Modern GUI interface (PyQt6)
- Standalone executable for Windows

## Requirements

- Python 3.7 or higher (for running from source)
- FFmpeg (for audio extraction and video processing)
- PyQt6 (for GUI version)

## Installation

### Option 1: Using the Executable (Windows)
1. Download the latest release from the [Releases](https://github.com/openvaibhav/youtube-downloader/releases) page
2. Extract the zip file
3. Run `YouTube Downloader.exe`

### Option 2: Running from Source
1. Clone this repository:
```bash
git clone https://github.com/openvaibhav/youtube-downloader.git
cd youtube-downloader
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Install FFmpeg:
   - Windows: Download from [FFmpeg website](https://ffmpeg.org/download.html)
   - Linux: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo pacman -S ffmpeg` (Arch)
   - macOS: `brew install ffmpeg`

## Usage

### GUI Version
1. Run the program:
```bash
python youtube_downloader_gui.py
```

2. Enter the YouTube URL
3. Select download type (Video or Audio)
4. Choose resolution (for video) or bitrate (for audio)
5. Select output directory (optional)
6. Click Download

### Command Line Version
1. Run the program:
```bash
python youtube_downloader.py
```

2. Choose your download type:
   - Enter `1` for video download
   - Enter `2` for audio download

3. Enter the YouTube URL (can be a single video or a playlist)

4. The files will be downloaded to the `downloads` folder in the same directory as the script

## Notes

- For audio downloads, the program will first download the video in highest quality and then extract the audio
- All downloaded files will be saved in the `downloads` directory
- The program handles both individual videos and playlists automatically
- Make sure you have sufficient disk space for downloads
- The program respects YouTube's terms of service and is for personal use only
- FFmpeg is required for video processing and audio extraction

## Building the Executable

To build the executable yourself:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Run the build command:
```bash
pyinstaller youtube_downloader.spec
```

The executable will be created in the `dist` folder.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 