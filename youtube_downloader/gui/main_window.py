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
        layout.addWidget(self.format_combo)
        
        # Quality selection section
        quality_label = QLabel(self.texts["quality_label"])
        quality_label.setFont(QFont("Arial", 12))
        layout.addWidget(quality_label)
        
        # Dropdown for video quality options
        self.quality_combo = QComboBox()
        self.populate_quality_options()
        layout.addWidget(self.quality_combo)
        
        # Download action button
        self.download_button = QPushButton(self.texts["download_button"])
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button)
        
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
        """Populate quality dropdown with localized options."""
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
        
        # Lock download button and show progress bar
        self.download_button.setEnabled(False)
        self.download_button.setText(self.texts.get("downloading_button", "Downloading..."))
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
    
    def download_finished(self, success, message):
        """
        Handle download completion, update UI and show result dialog.
        
        Args:
            success (bool): Whether download completed successfully
            message (str): Completion message or error details
        """
        # Re-enable download button and hide progress bar
        self.download_button.setEnabled(True)
        self.download_button.setText(self.texts["download_button"])
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        
        if success:
            # Update status for successful download
            self.status_label.setText(self.texts["download_complete"])
            self.status_label.setStyleSheet("color: green;")
            QMessageBox.information(self, self.texts["success"], self.texts["download_complete"])
        else:
            # Update status for failed download
            self.status_label.setText(self.texts["download_failed"])
            self.status_label.setStyleSheet("color: red;")
            QMessageBox.critical(self, self.texts["error"], message)