import yt_dlp
import os
from moviepy.editor import VideoFileClip
import re
import time
import random
import ssl
import certifi
import subprocess

# Use certifi's certificate bundle
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

def sanitize_filename(filename):
    # Remove invalid characters from filename
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
    ]
    return random.choice(user_agents)

def get_download_path():
    default_path = os.path.join(os.getcwd(), 'downloads')
    print(f"\nCurrent download path: {default_path}")
    choice = input("Do you want to change the download location? (y/n): ").lower()
    
    if choice == 'y':
        new_path = input("Enter the full path where you want to save the files: ")
        # Create the directory if it doesn't exist
        if not os.path.exists(new_path):
            os.makedirs(new_path)
        return new_path
    return default_path

class MyLogger:
    def debug(self, msg):
        # For compatibility with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        if msg.startswith('[debug] '):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        print(msg)

    def warning(self, msg):
        print(f"Warning: {msg}")

    def error(self, msg):
        print(f"Error: {msg}")

def download_video(url, output_path, resolution='best'):
    try:
        # Create downloads directory if it doesn't exist
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Format selection based on resolution
        format_selector = {
            'best': 'best[ext=mp4]',
            '1080p': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]',
            '720p': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]',
            '480p': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]',
            '360p': 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]'
        }

        ydl_opts = {
            'format': format_selector.get(resolution, 'best[ext=mp4]'),
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'user_agent': get_random_user_agent(),
            'extract_flat': True,
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': True,
            'ignoreerrors': True,
            'sleep_interval': 1,
            'max_sleep_interval': 5,
            'http_headers': {
                'User-Agent': get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            'logger': MyLogger(),
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            if 'playlist' in url.lower():
                print("Downloading playlist...")
                ydl.download([url])
            else:
                print("Downloading video...")
                ydl.download([url])

        # Check if any files were downloaded
        files = os.listdir(output_path)
        if not files:
            print("\nNo files were downloaded. There might be an issue with the URL or the download process.")
        else:
            print(f"\nDownload completed! Files are saved in: {output_path}")
            print("Downloaded files:")
            for file in files:
                print(f"- {file}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

def download_audio(url, output_path, bitrate='192'):
    try:
        # Create downloads directory if it doesn't exist
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Verify FFmpeg is available
        ffmpeg_path = os.path.join(os.getcwd(), 'ffmpeg.exe')
        if not os.path.exists(ffmpeg_path):
            raise Exception("FFmpeg not found. Please ensure ffmpeg.exe is in the same directory as this script.")

        print(f"Using FFmpeg at: {ffmpeg_path}")

        def convert_to_mp3(input_file, bitrate):
            output_file = os.path.join(output_path, os.path.splitext(os.path.basename(input_file))[0] + '.mp3')
            print(f"Converting {os.path.basename(input_file)} to MP3 with {bitrate}k bitrate...")
            try:
                subprocess.run([
                    ffmpeg_path,
                    '-i', input_file,
                    '-vn',
                    '-acodec', 'libmp3lame',
                    '-ab', f'{bitrate}k',
                    '-ar', '44100',
                    '-y',
                    output_file
                ], check=True)
                print(f"Successfully converted {os.path.basename(input_file)} to MP3")
                # Remove the original file
                os.remove(input_file)
                return True
            except subprocess.CalledProcessError as e:
                print(f"Error converting {os.path.basename(input_file)}: {str(e)}")
                return False

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': bitrate,
            }],
            'quiet': False,
            'no_warnings': False,
            'user_agent': get_random_user_agent(),
            'extract_flat': True,
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': True,
            'ignoreerrors': True,
            'sleep_interval': 1,
            'max_sleep_interval': 5,
            'http_headers': {
                'User-Agent': get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            'logger': MyLogger(),
            'ffmpeg_location': ffmpeg_path,
            'verbose': True,
            'postprocessor_args': {
                'FFmpegExtractAudio': {
                    'preferredcodec': 'mp3',
                    'preferredquality': bitrate,
                }
            },
            'keepvideo': False,
            'progress_hooks': [lambda d: print(f"\rDownloading: {d.get('filename', '')} - {d.get('_percent_str', '')}", end='')],
        }

        print("Starting download...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            if 'playlist' in url.lower():
                print("Downloading playlist...")
                # First get the playlist info
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    total_videos = len(info['entries'])
                    print(f"Found {total_videos} videos in playlist")
                    
                    # Download each video individually
                    for i, entry in enumerate(info['entries'], 1):
                        print(f"\nProcessing video {i}/{total_videos}: {entry.get('title', 'Unknown Title')}")
                        try:
                            # Download the video
                            ydl.download([entry['url']])
                            
                            # Find the downloaded file
                            files = [f for f in os.listdir(output_path) if f.endswith(('.webm', '.m4a'))]
                            if files:
                                # Convert the most recently downloaded file
                                latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(output_path, x)))
                                convert_to_mp3(os.path.join(output_path, latest_file), bitrate)
                        except Exception as e:
                            print(f"Error processing video {i}: {str(e)}")
                            continue
            else:
                print("Downloading single video...")
                ydl.download([url])
                # Convert any downloaded files
                files = [f for f in os.listdir(output_path) if f.endswith(('.webm', '.m4a'))]
                for file in files:
                    convert_to_mp3(os.path.join(output_path, file), bitrate)

        # Final check of downloaded files
        files = os.listdir(output_path)
        if not files:
            print("\nNo files were downloaded. There might be an issue with the URL or the download process.")
        else:
            print(f"\nDownload completed! Files are saved in: {output_path}")
            print("Downloaded MP3 files:")
            mp3_files = [f for f in files if f.endswith('.mp3')]
            if mp3_files:
                for file in mp3_files:
                    print(f"- {file}")
            else:
                print("No MP3 files were created. Check the output directory for other file formats.")
                print("All files in directory:")
                for file in files:
                    print(f"- {file}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        if "ffmpeg" in str(e).lower():
            print("\nFFmpeg error detected. Please ensure ffmpeg.exe is in the same directory as this script.")

def main():
    print("YouTube Downloader")
    print("1. Download Video")
    print("2. Download Audio")
    choice = input("Enter your choice (1 or 2): ")
    
    # Get download path
    download_path = get_download_path()
    
    url = input("Enter YouTube URL (video or playlist): ")
    
    if choice == "1":
        print("\nAvailable resolutions:")
        print("1. Best Quality")
        print("2. 1080p")
        print("3. 720p")
        print("4. 480p")
        print("5. 360p")
        res_choice = input("Enter resolution choice (1-5): ")
        
        resolution_map = {
            '1': 'best',
            '2': '1080p',
            '3': '720p',
            '4': '480p',
            '5': '360p'
        }
        
        resolution = resolution_map.get(res_choice, 'best')
        download_video(url, download_path, resolution)
    elif choice == "2":
        print("\nAvailable audio qualities:")
        print("1. Best Quality (320k)")
        print("2. High Quality (256k)")
        print("3. Medium Quality (192k)")
        print("4. Standard Quality (128k)")
        print("5. Low Quality (96k)")
        bitrate_choice = input("Enter audio quality choice (1-5): ")
        
        bitrate_map = {
            '1': '320',
            '2': '256',
            '3': '192',
            '4': '128',
            '5': '96'
        }
        
        bitrate = bitrate_map.get(bitrate_choice, '192')
        download_audio(url, download_path, bitrate)
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main() 