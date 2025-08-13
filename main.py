"""
YouTube Video Downloader with PyQt6 GUI - Main Entry Point

A modern GUI application for downloading YouTube videos and playlists with support for
multiple languages, formats (MP4/WEBM/MP3/WAV), and quality options. Built using PyQt6 for a
professional, cross-platform desktop experience.

Usage:
    python main.py

Dependencies: PyQt6, yt-dlp, ffmpeg, imageio-ffmpeg
"""

import sys
from PyQt6.QtWidgets import QApplication, QDialog

from youtube_downloader.gui import LanguageSelectorDialog, VideoDownloaderApp


def main():
    """
    Main application entry point.
    
    Creates the QApplication instance, shows the language selector dialog,
    and then launches the main video downloader window based on the user's
    language choice.
    """
    # Create the main Qt application instance
    app = QApplication(sys.argv)
    
    # Show language selector dialog first
    language_dialog = LanguageSelectorDialog()
    if language_dialog.exec() == QDialog.DialogCode.Accepted:
        # User selected a language and clicked Proceed
        selected_language = language_dialog.selected_language
        
        # Create and display the main application window
        main_window = VideoDownloaderApp(selected_language)
        main_window.show()
        
        # Start the Qt event loop and exit when application closes
        sys.exit(app.exec())
    # If user closed language dialog without selecting, application exits


if __name__ == "__main__":
    main()