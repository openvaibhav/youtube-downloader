import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLineEdit, QLabel, 
                           QComboBox, QProgressBar, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon
from pytube import YouTube
import re
import subprocess
import threading
import time

class DownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, url, output_path, video_resolution, audio_bitrate):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.video_resolution = video_resolution
        self.audio_bitrate = audio_bitrate

    def run(self):
        try:
            yt = YouTube(self.url, on_progress_callback=self.progress_callback)
            video_stream = yt.streams.filter(res=self.video_resolution, file_extension='mp4').first()
            audio_stream = yt.streams.filter(only_audio=True, abr=self.audio_bitrate).first()

            if not video_stream or not audio_stream:
                self.error.emit("Selected streams not available")
                return

            video_path = os.path.join(self.output_path, f"video_{int(time.time())}.mp4")
            audio_path = os.path.join(self.output_path, f"audio_{int(time.time())}.mp3")

            video_stream.download(output_path=self.output_path, filename=os.path.basename(video_path))
            audio_stream.download(output_path=self.output_path, filename=os.path.basename(audio_path))

            output_file = os.path.join(self.output_path, f"{yt.title}_{int(time.time())}.mp4")
            output_file = re.sub(r'[<>:"/\\|?*]', '_', output_file)

            ffmpeg_cmd = [
                'ffmpeg', '-i', video_path, '-i', audio_path,
                '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental',
                output_file
            ]

            process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.communicate()

            os.remove(video_path)
            os.remove(audio_path)

            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    def progress_callback(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = int((bytes_downloaded / total_size) * 100)
        self.progress.emit(percentage)

class YouTubeDownloaderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Downloader")
        self.setMinimumSize(600, 400)
        self.setWindowIcon(QIcon("icon.png"))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.setup_ui()
        self.download_thread = None

    def setup_ui(self):
        url_layout = QHBoxLayout()
        self.url_label = QLabel("YouTube URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube URL")
        url_layout.addWidget(self.url_label)
        url_layout.addWidget(self.url_input)
        self.layout.addLayout(url_layout)

        resolution_layout = QHBoxLayout()
        self.resolution_label = QLabel("Video Resolution:")
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["1080p", "720p", "480p", "360p"])
        resolution_layout.addWidget(self.resolution_label)
        resolution_layout.addWidget(self.resolution_combo)
        self.layout.addLayout(resolution_layout)

        bitrate_layout = QHBoxLayout()
        self.bitrate_label = QLabel("Audio Bitrate:")
        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems(["160kbps", "128kbps", "70kbps", "50kbps"])
        bitrate_layout.addWidget(self.bitrate_label)
        bitrate_layout.addWidget(self.bitrate_combo)
        self.layout.addLayout(bitrate_layout)

        path_layout = QHBoxLayout()
        self.path_label = QLabel("Download Path:")
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        self.path_input.setText(os.path.join(os.path.expanduser("~"), "Downloads"))
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_path)
        path_layout.addWidget(self.path_label)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_button)
        self.layout.addLayout(path_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.progress_bar)

        button_layout = QHBoxLayout()
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.start_download)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_download)
        self.cancel_button.setEnabled(False)
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)

    def browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Download Directory")
        if path:
            self.path_input.setText(path)

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a YouTube URL")
            return

        output_path = self.path_input.text()
        video_resolution = self.resolution_combo.currentText()
        audio_bitrate = self.bitrate_combo.currentText()

        self.download_thread = DownloadThread(url, output_path, video_resolution, audio_bitrate)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.error.connect(self.show_error)

        self.download_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setValue(0)

        self.download_thread.start()

    def cancel_download(self):
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.terminate()
            self.download_thread.wait()
            self.reset_ui()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def download_finished(self):
        QMessageBox.information(self, "Success", "Download completed successfully!")
        self.reset_ui()

    def show_error(self, error_message):
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")
        self.reset_ui()

    def reset_ui(self):
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(0)

def main():
    app = QApplication(sys.argv)
    window = YouTubeDownloaderGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 