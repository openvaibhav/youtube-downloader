import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLineEdit, QLabel, 
                           QComboBox, QProgressBar, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import yt_dlp
from moviepy.editor import VideoFileClip
import re

class DownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, url, download_type, output_path, resolution=None, bitrate=None):
        super().__init__()
        self.url = url
        self.download_type = download_type
        self.output_path = output_path
        self.resolution = resolution
        self.bitrate = bitrate

    def run(self):
        try:
            if self.download_type == "Video":
                self.download_video()
            else:
                self.download_audio()
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    def download_video(self):
        # Set format string for resolution
        fmt = f'bestvideo[height<={self.resolution}]+bestaudio/best[height<={self.resolution}]' if self.resolution else 'best'
        ydl_opts = {
            'format': fmt,
            'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])

    def download_audio(self):
        # First download the video
        temp_path = os.path.join(self.output_path, 'temp')
        os.makedirs(temp_path, exist_ok=True)
        # Set audio quality
        audio_quality = self.bitrate if self.bitrate else '192'
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(temp_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': audio_quality,
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(self.url, download=True)
            video_path = os.path.join(temp_path, f"{info['title']}.{info['ext']}")
            # Convert to audio (if not already done by yt-dlp)
            audio_path = os.path.join(self.output_path, f"{info['title']}.mp3")
            if not os.path.exists(audio_path):
                video = VideoFileClip(video_path)
                video.audio.write_audiofile(audio_path, bitrate=f'{audio_quality}k')
                video.close()
                os.remove(video_path)
            # Clean up
            if os.path.exists(video_path):
                os.remove(video_path)
            os.rmdir(temp_path)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                p = d['_percent_str']
                p = p.replace('%', '')
                self.progress.emit(int(float(p)))
            except:
                pass

class YouTubeDownloaderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Downloader")
        self.setMinimumSize(600, 400)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # URL input
        url_layout = QHBoxLayout()
        url_label = QLabel("YouTube URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube URL or playlist URL")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)
        
        # Download type selection
        type_layout = QHBoxLayout()
        type_label = QLabel("Download Type:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Video", "Audio"])
        self.type_combo.currentTextChanged.connect(self.toggle_options)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # Resolution selection for video
        self.resolution_layout = QHBoxLayout()
        self.resolution_label = QLabel("Resolution:")
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["2160", "1440", "1080", "720", "480", "360", "240", "144"])  # Common YouTube resolutions
        self.resolution_layout.addWidget(self.resolution_label)
        self.resolution_layout.addWidget(self.resolution_combo)
        layout.addLayout(self.resolution_layout)
        
        # Bitrate selection for audio
        self.bitrate_layout = QHBoxLayout()
        self.bitrate_label = QLabel("Bitrate (kbps):")
        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems(["320", "256", "192", "128", "96", "64"])
        self.bitrate_layout.addWidget(self.bitrate_label)
        self.bitrate_layout.addWidget(self.bitrate_combo)
        layout.addLayout(self.bitrate_layout)
        
        # Output directory selection
        dir_layout = QHBoxLayout()
        dir_label = QLabel("Output Directory:")
        self.dir_input = QLineEdit()
        self.dir_input.setReadOnly(True)
        self.dir_input.setText(os.path.join(os.getcwd(), "downloads"))
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_directory)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(browse_button)
        layout.addLayout(dir_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Download button
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button)
        
        # Status label
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        
        # Create downloads directory if it doesn't exist
        os.makedirs(self.dir_input.text(), exist_ok=True)
        self.toggle_options(self.type_combo.currentText())

    def toggle_options(self, download_type):
        if download_type == "Video":
            self.resolution_label.show()
            self.resolution_combo.show()
            self.bitrate_label.hide()
            self.bitrate_combo.hide()
        else:
            self.resolution_label.hide()
            self.resolution_combo.hide()
            self.bitrate_label.show()
            self.bitrate_combo.show()

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.dir_input.setText(directory)
            os.makedirs(directory, exist_ok=True)

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a YouTube URL")
            return
            
        self.download_button.setEnabled(False)
        self.status_label.setText("Downloading...")
        self.progress_bar.setValue(0)
        
        download_type = self.type_combo.currentText()
        resolution = self.resolution_combo.currentText() if download_type == "Video" else None
        bitrate = self.bitrate_combo.currentText() if download_type == "Audio" else None
        
        self.download_thread = DownloadThread(
            url,
            download_type,
            self.dir_input.text(),
            resolution,
            bitrate
        )
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.error.connect(self.download_error)
        self.download_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def download_finished(self):
        self.download_button.setEnabled(True)
        self.status_label.setText("Download completed!")
        QMessageBox.information(self, "Success", "Download completed successfully!")

    def download_error(self, error_message):
        self.download_button.setEnabled(True)
        self.status_label.setText("Error occurred!")
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YouTubeDownloaderGUI()
    window.show()
    sys.exit(app.exec()) 