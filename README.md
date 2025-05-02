# YouTube Downloader

A simple Python program to download YouTube videos or extract audio from videos and playlists.

## Features

- Download individual YouTube videos
- Download entire playlists
- Choose between video or audio format
- Automatic creation of downloads directory
- Sanitized filenames for compatibility
- Support for high-quality video downloads
- Progress tracking for downloads

## Requirements

- Python 3.7 or higher
- FFmpeg (for audio extraction)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/youtube-downloader.git
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

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 