"""
Main application window for the YouTube Downloader.

Contains the VideoDownloaderApp class which provides the main GUI interface
with input fields, format selection, quality options, and download functionality.
"""

import os
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QMessageBox, QMenu, 
                             QProgressBar, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtWidgets import QApplication

from ..localization import get_texts
from ..core import DownloadThread
from ..utils import is_playlist_url
from .dialogs import show_playlist_dialog


class VideoDownloaderApp(QMainWindow):
    """
    Main application window for the YouTube Video Downloader.
    
    This class creates the main GUI interface with input fields for URL,
    format selection, quality options, and download functionality. Includes
    playlist detection and user choice for playlist handling.
    """
    
    def __init__(self, language):
        """
        Initialize the main application window.
        
        Args:
            language (str): Selected language for UI text localization
        """
        super().__init__()
        self.language = language
        self.texts = get_texts(language)  # Load localized text strings
        
        # Configure main window properties
        self.setWindowTitle(self.texts["title"])
        self.setFixedSize(500, 450)  # Increased height for destination folder
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Application title label
        title_label = QLabel(self.texts["app_title"])
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # URL input section
        url_label = QLabel(self.texts["url_label"])
        url_label.setFont(QFont("Arial", 12))
        layout.addWidget(url_label)
        
        # URL text input field with context menu support
        self.url_entry = QLineEdit()
        self.url_entry.setFont(QFont("Arial", 10))
        self.setup_context_menu()  # Enable right-click paste/delete
        layout.addWidget(self.url_entry)
        
        # Destination folder section
        destination_label = QLabel(self.texts["destination_label"])
        destination_label.setFont(QFont("Arial", 12))
        layout.addWidget(destination_label)
        
        # Destination folder selection layout
        destination_layout = QHBoxLayout()
        
        # Destination folder display
        self.destination_entry = QLineEdit()
        self.destination_entry.setFont(QFont("Arial", 10))
        self.destination_entry.setText(os.getcwd())  # Default to current working directory
        self.destination_entry.setReadOnly(True)  # Read-only, user must use browse button
        destination_layout.addWidget(self.destination_entry)
        
        # Browse button for folder selection
        self.browse_button = QPushButton(self.texts["browse_button"])
        self.browse_button.clicked.connect(self.browse_destination)
        destination_layout.addWidget(self.browse_button)
        
        # Create widget for destination layout and add to main layout
        destination_widget = QWidget()
        destination_widget.setLayout(destination_layout)
        layout.addWidget(destination_widget)
        
        # Format selection section
        format_label = QLabel(self.texts["format_label"])
        format_label.setFont(QFont("Arial", 12))
        layout.addWidget(format_label)
        
        # Dropdown for format selection (video and audio options)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP4", "WEBM", "MP3", "WAV"])
        self.format_combo.setCurrentText("MP4")
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        layout.addWidget(self.format_combo)
        
        # Quality selection section
        quality_label = QLabel(self.texts["quality_label"])
        quality_label.setFont(QFont("Arial", 12))
        layout.addWidget(quality_label)
        
        # Dropdown for video quality options
        self.quality_combo = QComboBox()
        self.populate_quality_options()
        layout.addWidget(self.quality_combo)
        
        # Download and abort buttons layout
        button_layout = QHBoxLayout()
        
        # Download action button
        self.download_button = QPushButton(self.texts["download_button"])
        self.download_button.clicked.connect(self.start_download)
        button_layout.addWidget(self.download_button)
        
        # Abort download button (initially hidden)
        self.abort_button = QPushButton(self.texts.get("abort_button", "Abort"))
        self.abort_button.clicked.connect(self.abort_download)
        self.abort_button.setVisible(False)  # Hidden by default
        self.abort_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; }")
        button_layout.addWidget(self.abort_button)
        
        # Create widget for button layout and add to main layout
        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        layout.addWidget(button_widget)
        
        # Progress bar for download progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)  # Hidden by default
        layout.addWidget(self.progress_bar)
        
        # Status display label for download progress/results
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: green;")
        layout.addWidget(self.status_label)
    
    def populate_quality_options(self):
        """Populate quality dropdown with localized options based on selected format."""
        current_format = self.format_combo.currentText()
        
        # Clear existing options
        self.quality_combo.clear()
        
        if current_format in ["MP4", "WEBM"]:
            # Video formats get full quality options
            quality_options = [
                self.texts.get("quality_best", "Best"),
                "1080p", 
                "720p", 
                "480p", 
                "360p", 
                self.texts.get("quality_lowest", "Lowest")
            ]
            self.quality_combo.addItems(quality_options)
            self.quality_combo.setCurrentText(self.texts.get("quality_best", "Best"))
            self.quality_combo.setEnabled(True)
        else:
            # Audio formats (MP3/WAV) get audio-specific quality options
            audio_quality_options = [
                self.texts.get("audio_quality_high", "High Quality"),
                self.texts.get("audio_quality_medium", "Medium Quality"),
                self.texts.get("audio_quality_low", "Low Quality")
            ]
            self.quality_combo.addItems(audio_quality_options)
            self.quality_combo.setCurrentText(self.texts.get("audio_quality_high", "High Quality"))
            self.quality_combo.setEnabled(True)
    
    def on_format_changed(self):
        """Called when user changes format selection."""
        self.populate_quality_options()
    
    def setup_context_menu(self):
        """Configure right-click context menu for URL input field."""
        self.url_entry.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.url_entry.customContextMenuRequested.connect(self.show_context_menu)
    
    def show_context_menu(self, position):
        """
        Display context menu with paste and delete options.
        
        Args:
            position (QPoint): Position where right-click occurred
        """
        context_menu = QMenu(self)
        
        # Add paste option to context menu
        paste_action = QAction(self.texts['paste'], self)
        paste_action.triggered.connect(self.paste_from_clipboard)
        context_menu.addAction(paste_action)
        
        # Add delete/clear option to context menu
        delete_action = QAction(self.texts['delete'], self)
        delete_action.triggered.connect(self.delete_url_entry)
        context_menu.addAction(delete_action)
        
        # Show context menu at cursor position
        context_menu.exec(self.url_entry.mapToGlobal(position))
    
    def paste_from_clipboard(self):
        """Insert clipboard content into URL input field."""
        clipboard = QApplication.clipboard()
        self.url_entry.insert(clipboard.text())
    
    def delete_url_entry(self):
        """Clear all text from URL input field."""
        self.url_entry.clear()
    
    def browse_destination(self):
        """Open folder selection dialog for download destination."""
        current_dir = self.destination_entry.text()
        selected_dir = QFileDialog.getExistingDirectory(
            self, 
            self.texts["select_destination"], 
            current_dir
        )
        
        if selected_dir:  # User selected a folder (didn't cancel)
            self.destination_entry.setText(selected_dir)
    
    def start_download(self):
        """
        Initiate download process after validating input and checking for playlists.
        """
        video_url = self.url_entry.text().strip()
        
        # Validate that URL is provided
        if not video_url:
            QMessageBox.critical(self, self.texts["error"], self.texts["url_error"])
            return
        
        # Get selected format and quality options
        format_type = self.format_combo.currentText()
        quality = self.quality_combo.currentText()
        
        # Check if URL is a playlist and ask user preference
        is_playlist = False
        if is_playlist_url(video_url):
            is_playlist = show_playlist_dialog(self, self.texts)
        
        # Update UI for download state
        self.download_button.setEnabled(False)
        self.download_button.setText(self.texts.get("downloading_button", "Downloading..."))
        self.abort_button.setVisible(True)
        self.abort_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Get selected destination folder
        destination_folder = self.destination_entry.text()

        # Create and start download thread with playlist option and destination
        self.download_thread = DownloadThread(video_url, format_type, quality, self.texts, is_playlist, destination_folder)
        self.download_thread.status_update.connect(self.update_status)
        self.download_thread.progress_update.connect(self.update_progress)
        self.download_thread.download_complete.connect(self.download_finished)
        self.download_thread.start()
    
    def abort_download(self):
        """
        Abort the current download operation.
        """
        if hasattr(self, 'download_thread') and self.download_thread.isRunning():
            # Request thread termination
            self.download_thread.request_abort()
            
            # Update UI immediately
            self.abort_button.setEnabled(False)
            self.abort_button.setText(self.texts.get("aborting_button", "Aborting..."))
            self.update_status(self.texts.get("aborting_status", "Aborting download..."), "orange")
    
    def update_status(self, message, color):
        """
        Update status label with new message and color.
        
        Args:
            message (str): Status message to display
            color (str): CSS color name for text color
        """
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color};")
    
    def update_progress(self, progress):
        """
        Update progress bar with download progress.
        
        Args:
            progress (int): Progress percentage (0-100)
        """
        self.progress_bar.setValue(progress)
    
    def download_finished(self, success, message, failed_videos=None):
        """
        Handle download completion, update UI and show result dialog.
        
        Args:
            success (bool): Whether download completed successfully
            message (str): Completion message or error details
            failed_videos (list): List of failed video information (for playlists)
        """
        # Reset UI to initial state
        self.download_button.setEnabled(True)
        self.download_button.setText(self.texts["download_button"])
        self.abort_button.setVisible(False)
        self.abort_button.setEnabled(True)
        self.abort_button.setText(self.texts.get("abort_button", "Abort"))
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        
        if failed_videos is None:
            failed_videos = []
        
        if success and not failed_videos:
            # Complete success - update status for successful download
            self.status_label.setText(self.texts["download_complete"])
            self.status_label.setStyleSheet("color: green;")
            QMessageBox.information(self, self.texts["success"], self.texts["download_complete"])
        elif success and failed_videos:
            # Partial success - some videos failed
            self.status_label.setText(message)
            self.status_label.setStyleSheet("color: orange;")
            self.show_failed_videos_dialog(message, failed_videos)
        else:
            # Complete failure
            self.status_label.setText(self.texts["download_failed"])
            self.status_label.setStyleSheet("color: red;")
            if failed_videos:
                self.show_failed_videos_dialog(message, failed_videos)
            else:
                QMessageBox.critical(self, self.texts["error"], message)
    
    def show_failed_videos_dialog(self, main_message, failed_videos):
        """
        Show dialog with details about failed videos during playlist download.
        
        Args:
            main_message (str): Main completion message
            failed_videos (list): List of failed video information
        """
        # Create detailed message with failed video information
        failed_count = len(failed_videos)
        dialog_title = self.texts.get("partial_download_title", "Download Completed with Errors")
        
        # Build the message text
        message_parts = [main_message, ""]
        
        if failed_count > 0:
            failed_header = self.texts.get("failed_videos_header", f"The following {failed_count} videos failed to download:")
            message_parts.append(failed_header)
            message_parts.append("")
            
            for i, video in enumerate(failed_videos[:10], 1):  # Limit to first 10 failures
                video_title = video.get('title', 'Unknown Title')
                video_url = video.get('url', 'Unknown URL')
                error_type = self.get_error_type(video.get('error', ''))
                
                message_parts.append(f"{i}. {video_title}")
                if video_url and video_url != 'Unknown URL':
                    message_parts.append(f"   URL: {video_url}")
                message_parts.append(f"   Reason: {error_type}")
                message_parts.append("")
            
            if failed_count > 10:
                additional_count = failed_count - 10
                message_parts.append(self.texts.get("more_failures", f"... and {additional_count} more failures"))
        
        detailed_message = "\n".join(message_parts)
        
        # Show message box with detailed information
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(dialog_title)
        msg_box.setText(main_message)
        msg_box.setDetailedText(detailed_message)
        msg_box.setIcon(QMessageBox.Icon.Warning if failed_count < len(failed_videos) else QMessageBox.Icon.Critical)
        msg_box.exec()
    
    def get_error_type(self, error_message):
        """
        Extract user-friendly error type from yt-dlp error message.
        
        Args:
            error_message (str): Raw error message from yt-dlp
            
        Returns:
            str: User-friendly error description
        """
        error_message_lower = error_message.lower()
        
        if 'private video' in error_message_lower:
            return self.texts.get("error_private", "Private video")
        elif 'video unavailable' in error_message_lower:
            return self.texts.get("error_unavailable", "Video unavailable")
        elif 'does not exist' in error_message_lower:
            return self.texts.get("error_not_found", "Video not found")
        elif 'copyright' in error_message_lower:
            return self.texts.get("error_copyright", "Copyright restricted")
        elif 'geo' in error_message_lower or 'region' in error_message_lower:
            return self.texts.get("error_geo", "Geo-restricted content")
        elif 'age' in error_message_lower:
            return self.texts.get("error_age", "Age-restricted content")
        else:
            return self.texts.get("error_unknown", "Unknown error")