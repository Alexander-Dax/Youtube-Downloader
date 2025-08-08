"""
Download thread for handling video/playlist downloads in the background.

Contains the DownloadThread class that runs yt-dlp downloads in a separate
thread to prevent GUI freezing, with progress callbacks and status updates.
"""

import os
from PyQt6.QtCore import QThread, pyqtSignal
from yt_dlp import YoutubeDL
import certifi
import imageio_ffmpeg

from .format_handler import get_format_options


class DownloadThread(QThread):
    """
    Separate thread for handling video/playlist downloads.
    
    This thread runs the yt-dlp download process in the background to prevent
    the GUI from freezing during downloads. Emits signals to update the main
    thread with progress and completion status.
    """
    
    # Signal definitions for communication with main thread
    status_update = pyqtSignal(str, str)  # message, color
    progress_update = pyqtSignal(int)  # progress percentage (0-100)
    download_complete = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, video_url, format_type, quality, texts, is_playlist=False, destination_folder=None):
        """
        Initialize the download thread.
        
        Args:
            video_url (str): URL of the video or playlist to download
            format_type (str): Format selection - "MP4", "WEBM", "MP3", or "WAV"
            quality (str): Video quality selection (Best, 1080p, etc.) - may be localized
            texts (dict): Localized text strings for UI messages
            is_playlist (bool): Whether to download entire playlist or single video
            destination_folder (str): Path to download destination folder
        """
        super().__init__()
        self.video_url = video_url
        self.format_type = format_type
        self.quality = quality
        self.texts = texts
        self.is_playlist = is_playlist
        self.destination_folder = destination_folder or os.getcwd()
    
    def progress_hook(self, d):
        """
        Progress callback function for yt-dlp.
        
        Args:
            d (dict): Progress information from yt-dlp
        """
        if d['status'] == 'downloading':
            # Calculate progress percentage
            if 'total_bytes' in d and d['total_bytes']:
                downloaded = d.get('downloaded_bytes', 0)
                total = d['total_bytes']
                progress = int((downloaded / total) * 100)
                self.progress_update.emit(progress)
            elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                downloaded = d.get('downloaded_bytes', 0)
                total = d['total_bytes_estimate']
                progress = int((downloaded / total) * 100)
                self.progress_update.emit(progress)
        elif d['status'] == 'finished':
            # Download finished, set progress to 100%
            self.progress_update.emit(100)

    def run(self):
        """Main download execution method (runs in separate thread)."""
        try:
            # Update status to show download started and reset progress
            self.status_update.emit(self.texts["downloading"], "blue")
            self.progress_update.emit(0)
            
            # Get format and postprocessor options
            format_option, postprocessors = get_format_options(self.format_type, self.quality)

            # Get ffmpeg executable path for audio conversion
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

            # Generate output template with destination folder
            if self.format_type in ["MP4", "WEBM"]:
                filename_template = f'%(title)s-{self.quality}.%(ext)s'
            else:  # Audio formats
                filename_template = '%(title)s.%(ext)s'
            
            # Combine destination folder with filename template
            outtmpl = os.path.join(self.destination_folder, filename_template)

            # Configure yt-dlp download options with progress hook
            ydl_opts = {
                'format': format_option,
                'outtmpl': outtmpl,
                'postprocessors': postprocessors,
                'quiet': False,  # Set to True to suppress console output
                'ca_bundle': certifi.where(),  # SSL certificate bundle
                'ffmpeg_location': ffmpeg_path,
                'noplaylist': not self.is_playlist,  # Download playlist or single video
                'progress_hooks': [self.progress_hook]  # Add progress callback
            }

            # Execute download using yt-dlp
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.video_url])

            # Emit success signal
            self.download_complete.emit(True, self.texts["download_complete"])

        except Exception as e:
            # Emit error signal with exception details
            self.download_complete.emit(False, f"Failed to download the video: {str(e)}")