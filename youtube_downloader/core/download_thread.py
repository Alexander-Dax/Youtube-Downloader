"""
Download thread for handling video/playlist downloads in the background.

Contains the DownloadThread class that runs yt-dlp downloads in a separate
thread to prevent GUI freezing, with progress callbacks and status updates.
"""

import os
import re
from PyQt6.QtCore import QThread, pyqtSignal
from yt_dlp import YoutubeDL
import certifi
import imageio_ffmpeg

from .format_handler import get_format_options


class PlaylistErrorTracker:
    """
    Custom logger to track failed downloads during playlist processing.
    """
    
    def __init__(self):
        self.failed_videos = []
        self.successful_videos = []
        self.skipped_videos = []
        self.warnings = []
    
    def debug(self, msg):
        """Handle debug messages from yt-dlp."""
        pass  # Keep debug messages quiet
    
    def info(self, msg):
        """Handle info messages from yt-dlp."""
        # Track successful downloads
        if '[download] Destination:' in msg:
            video_id = self._extract_video_id_from_msg(msg)
            title = self._extract_title_from_msg(msg)
            if video_id and not any(v['id'] == video_id for v in self.successful_videos):
                self.successful_videos.append({
                    'id': video_id,
                    'title': title,
                    'message': msg
                })
        # Track skipped files (already downloaded)
        elif 'has already been downloaded' in msg or 'Skipping' in msg:
            video_id = self._extract_video_id_from_msg(msg)
            title = self._extract_title_from_msg(msg) if '[download] Destination:' not in msg else self._extract_skipped_title(msg)
            if video_id and not any(v['id'] == video_id for v in self.skipped_videos):
                self.skipped_videos.append({
                    'id': video_id,
                    'title': title,
                    'message': msg
                })
    
    def warning(self, msg):
        """Handle warning messages from yt-dlp."""
        self.warnings.append(msg)
        # Filter out known SABR streaming warnings to reduce noise
        if not ('SABR streaming' in msg or 'missing a url' in msg):
            print(f"WARNING: {msg}")
    
    def error(self, msg):
        """Handle error messages from yt-dlp."""
        # Extract video information from error messages
        video_info = self._extract_error_info(msg)
        if video_info:
            self.failed_videos.append(video_info)
        print(f"ERROR: {msg}")
    
    def _extract_video_id_from_msg(self, msg):
        """Extract video ID from various yt-dlp messages."""
        # Look for YouTube video ID pattern
        match = re.search(r'[a-zA-Z0-9_-]{11}', msg)
        return match.group(0) if match else None
    
    def _extract_title_from_msg(self, msg):
        """Extract video title from yt-dlp messages."""
        # Extract title from destination path
        if '[download] Destination:' in msg:
            # Extract filename without extension and quality suffix
            filename = os.path.basename(msg.split('Destination: ')[1])
            # Remove quality suffix and extension
            title = re.sub(r'-\w+\.\w+$', '', filename)
            return title
        return "Unknown Title"
    
    def _extract_skipped_title(self, msg):
        """Extract video title from skipped video messages."""
        # Handle "has already been downloaded" messages
        if 'has already been downloaded' in msg:
            # Extract video ID and create a basic title
            video_id = self._extract_video_id_from_msg(msg)
            return f"Video {video_id}" if video_id else "Previously Downloaded Video"
        return "Skipped Video"
    
    def _extract_error_info(self, msg):
        """Extract video information from error messages."""
        video_info = {
            'id': 'unknown',
            'title': 'Unknown Video',
            'error': msg,
            'url': None
        }
        
        # Extract video ID from various error message formats
        id_match = re.search(r'[a-zA-Z0-9_-]{11}', msg)
        if id_match:
            video_info['id'] = id_match.group(0)
            video_info['url'] = f"https://www.youtube.com/watch?v={video_info['id']}"
        
        # Extract title if available in error message
        if 'Video unavailable' in msg or 'Private video' in msg:
            video_info['title'] = 'Unavailable/Private Video'
        elif 'does not exist' in msg:
            video_info['title'] = 'Video Does Not Exist'
        
        return video_info if video_info['id'] != 'unknown' else None


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
    download_complete = pyqtSignal(bool, str, list)  # success, message, failed_videos
    
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
        self.error_tracker = PlaylistErrorTracker()
        self.abort_requested = False
        
        # Create download archive file path for tracking downloaded videos
        self.archive_file = os.path.join(self.destination_folder, '.yt-dlp-archive.txt')
    
    def request_abort(self):
        """
        Request that the download be aborted.
        """
        self.abort_requested = True
    
    def progress_hook(self, d):
        """
        Progress callback function for yt-dlp.
        
        Args:
            d (dict): Progress information from yt-dlp
        """
        # Check for abort request
        if self.abort_requested:
            # Signal yt-dlp to stop by raising an exception
            raise KeyboardInterrupt("Download aborted by user")
        
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
            # Check for abort before starting
            if self.abort_requested:
                self.download_complete.emit(False, self.texts.get("download_aborted", "Download was aborted"), [])
                return
            
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

            # Configure yt-dlp download options with progress hook and error handling
            ydl_opts = {
                'format': format_option,
                'outtmpl': outtmpl,
                'postprocessors': postprocessors,
                'quiet': False,  # Set to True to suppress console output
                'ca_bundle': certifi.where(),  # SSL certificate bundle
                'ffmpeg_location': ffmpeg_path,
                'noplaylist': not self.is_playlist,  # Download playlist or single video
                'progress_hooks': [self.progress_hook],  # Add progress callback
                'logger': self.error_tracker,  # Add custom error tracker
                'ignoreerrors': True,  # Continue downloading when individual videos fail
                'no_warnings': False,  # Keep warnings for debugging
                'extractor_retries': 3,  # Retry failed extractions
                'fragment_retries': 10,  # Retry failed fragments
                'file_access_retries': 3,  # Retry file access
                'sleep_interval': 1,  # Sleep between retries
                'max_sleep_interval': 5,  # Maximum sleep interval
                # File skipping options
                'download_archive': self.archive_file,  # Track downloaded videos
                'nooverwrites': True,  # Don't overwrite existing files
                'continue': True,  # Resume partial downloads
                'nopostoverwrites': True,  # Don't overwrite post-processed files
                # YouTube client configuration to avoid SABR streaming issues
                # See: https://github.com/yt-dlp/yt-dlp/issues/12482
                'extractor_args': {
                    'youtube': {
                        # Use clients that avoid SABR streaming enforcement
                        # tv_embedded: Most reliable, rarely affected by SABR issues
                        # android/ios: Mobile clients with good format availability  
                        # mweb: Mobile web client as fallback
                        'player_client': ['tv_embedded', 'android', 'ios', 'mweb'],
                        'formats': ['incomplete'],  # Allow incomplete formats for better availability
                    }
                }
            }

            # Execute download using yt-dlp
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.video_url])

            # Check if download was aborted during processing
            if self.abort_requested:
                self.download_complete.emit(False, self.texts.get("download_aborted", "Download was aborted"), [])
                return

            # Check if there were any failures or skips during playlist download
            failed_videos = self.error_tracker.failed_videos
            skipped_videos = self.error_tracker.skipped_videos
            successful_count = len(self.error_tracker.successful_videos)
            failed_count = len(failed_videos)
            skipped_count = len(skipped_videos)
            total_count = successful_count + failed_count + skipped_count

            # Determine success status and message
            if failed_count == 0 and skipped_count == 0:
                # Complete success - all new downloads
                success_msg = self.texts["download_complete"]
                self.download_complete.emit(True, success_msg, [])
            elif failed_count == 0 and skipped_count > 0:
                # Success with skips - no failures
                if self.is_playlist and skipped_count > 0:
                    success_msg = self.texts.get("download_with_skips", 
                        f"Download completed. {successful_count} downloaded, {skipped_count} already existed")
                else:
                    success_msg = self.texts.get("download_skipped", "File already exists, skipped download")
                self.download_complete.emit(True, success_msg, [])
            elif successful_count > 0 or skipped_count > 0:
                # Mixed results - some successful/skipped, some failed
                if self.is_playlist:
                    success_msg = self.texts.get("download_mixed_results", 
                        f"Download completed: {successful_count} downloaded, {skipped_count} skipped, {failed_count} failed")
                else:
                    success_msg = self.texts["download_failed"]
                self.download_complete.emit(successful_count > 0, success_msg, failed_videos)
            else:
                # Complete failure - no videos downloaded or skipped (all failed)
                failure_msg = self.texts.get("download_all_failed", "All videos failed to download")
                self.download_complete.emit(False, failure_msg, failed_videos)

        except KeyboardInterrupt:
            # Handle user abort request
            failed_videos = self.error_tracker.failed_videos if hasattr(self, 'error_tracker') else []
            self.download_complete.emit(False, self.texts.get("download_aborted", "Download was aborted"), failed_videos)
        except Exception as e:
            # Emit error signal with exception details and any tracked failures
            failed_videos = self.error_tracker.failed_videos if hasattr(self, 'error_tracker') else []
            if self.abort_requested:
                self.download_complete.emit(False, self.texts.get("download_aborted", "Download was aborted"), failed_videos)
            else:
                self.download_complete.emit(False, f"Failed to download the video: {str(e)}", failed_videos)