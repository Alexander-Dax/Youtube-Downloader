"""
YouTube Video Downloader with PyQt6 GUI

A modern GUI application for downloading YouTube videos and playlists with support for
multiple languages, formats (MP4/MP3), and quality options. Built using PyQt6 for a
professional, cross-platform desktop experience.

Author: Enhanced with PyQt6
Dependencies: PyQt6, yt-dlp, ffmpeg, imageio-ffmpeg
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QLineEdit, QComboBox, QPushButton, 
                             QMessageBox, QDialog, QMenu)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QAction
import ffmpeg._utils
from yt_dlp import YoutubeDL
import certifi
import imageio_ffmpeg
import re


class LanguageSelectorDialog(QDialog):
    """
    Initial dialog window for language selection.
    
    This dialog appears when the application starts, allowing users to choose
    their preferred language for the main application interface. Supports
    German, English, Spanish, and French.
    """
    
    def __init__(self):
        """Initialize the language selection dialog."""
        super().__init__()
        self.setWindowTitle("Select Language")
        self.setFixedSize(300, 200)
        self.selected_language = "Deutsch"  # Default language
        
        # Create main layout
        layout = QVBoxLayout()
        
        # Title label with bold font
        title_label = QLabel("Choose Language")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Language dropdown with available languages
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Deutsch", "English", "Español", "Français"])
        self.language_combo.setCurrentText("Deutsch")
        layout.addWidget(self.language_combo)
        
        # Proceed button to continue to main application
        proceed_button = QPushButton("Proceed")
        proceed_button.clicked.connect(self.proceed_to_app)
        layout.addWidget(proceed_button)
        
        self.setLayout(layout)
    
    def proceed_to_app(self):
        """Store selected language and close dialog."""
        self.selected_language = self.language_combo.currentText()
        self.accept()  # Close dialog with accepted status


class DownloadThread(QThread):
    """
    Separate thread for handling video/playlist downloads.
    
    This thread runs the yt-dlp download process in the background to prevent
    the GUI from freezing during downloads. Emits signals to update the main
    thread with progress and completion status.
    """
    
    # Signal definitions for communication with main thread
    status_update = pyqtSignal(str, str)  # message, color
    download_complete = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, video_url, format_type, quality, texts, is_playlist=False):
        """
        Initialize the download thread.
        
        Args:
            video_url (str): URL of the video or playlist to download
            format_type (str): "MP4" for video or "MP3" for audio only
            quality (str): Video quality selection (Best, 1080p, etc.)
            texts (dict): Localized text strings for UI messages
            is_playlist (bool): Whether to download entire playlist or single video
        """
        super().__init__()
        self.video_url = video_url
        self.format_type = format_type
        self.quality = quality
        self.texts = texts
        self.is_playlist = is_playlist
    
    def run(self):
        """Main download execution method (runs in separate thread)."""
        try:
            # Update status to show download started
            self.status_update.emit(self.texts["downloading"], "blue")
            
            # Map quality selections to yt-dlp format strings
            quality_map = {
                "Best": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
                "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]",
                "720p": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]",
                "480p": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]",
                "360p": "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]",
                "Lowest": "worst[ext=mp4]",
            }
            quality_option = quality_map[self.quality]

            # Get ffmpeg executable path for audio conversion
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

            # Configure yt-dlp download options
            ydl_opts = {
                'format': quality_option,
                'outtmpl': f'%(title)s-{self.quality}.%(ext)s' if self.format_type == "MP4" else '%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }] if self.format_type == "MP3" else [],
                'quiet': False,  # Set to True to suppress console output
                'ca_bundle': certifi.where(),  # SSL certificate bundle
                'ffmpeg_location': ffmpeg_path,
                'noplaylist': not self.is_playlist  # Download playlist or single video
            }

            # Execute download using yt-dlp
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.video_url])

            # Emit success signal
            self.download_complete.emit(True, self.texts["download_complete"])

        except Exception as e:
            # Emit error signal with exception details
            self.download_complete.emit(False, f"Failed to download the video: {str(e)}")


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
        self.texts = self.get_texts(language)  # Load localized text strings
        
        # Configure main window properties
        self.setWindowTitle(self.texts["title"])
        self.setFixedSize(500, 400)
        
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
        
        # Format selection section
        format_label = QLabel(self.texts["format_label"])
        format_label.setFont(QFont("Arial", 12))
        layout.addWidget(format_label)
        
        # Dropdown for MP4 video or MP3 audio selection
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP4", "MP3"])
        self.format_combo.setCurrentText("MP4")
        layout.addWidget(self.format_combo)
        
        # Quality selection section
        quality_label = QLabel(self.texts["quality_label"])
        quality_label.setFont(QFont("Arial", 12))
        layout.addWidget(quality_label)
        
        # Dropdown for video quality options
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Best", "1080p", "720p", "480p", "360p", "Lowest"])
        self.quality_combo.setCurrentText("Best")
        layout.addWidget(self.quality_combo)
        
        # Download action button
        download_button = QPushButton(self.texts["download_button"])
        download_button.clicked.connect(self.start_download)
        layout.addWidget(download_button)
        
        # Status display label for download progress/results
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: green;")
        layout.addWidget(self.status_label)
    
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
    
    def is_playlist_url(self, url):
        """
        Check if the provided URL is a YouTube playlist.
        
        Args:
            url (str): URL to check
            
        Returns:
            bool: True if URL contains playlist indicators, False otherwise
        """
        # Common YouTube playlist URL patterns
        playlist_patterns = [
            r'[?&]list=',  # Standard playlist parameter
            r'/playlist\?',  # Direct playlist URL
            r'[?&]index=',  # Video index in playlist
        ]
        
        return any(re.search(pattern, url, re.IGNORECASE) for pattern in playlist_patterns)
    
    def show_playlist_dialog(self):
        """
        Show dialog asking user whether to download playlist or single video.
        
        Returns:
            bool: True if user wants to download full playlist, False for single video
        """
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle(self.texts.get("playlist_detected", "Playlist Detected"))
        msg.setText(self.texts.get("playlist_question", 
                   "This appears to be a playlist URL. What would you like to download?"))
        
        # Add custom buttons
        playlist_button = msg.addButton(
            self.texts.get("download_playlist", "Download Entire Playlist"), 
            QMessageBox.ButtonRole.YesRole
        )
        single_button = msg.addButton(
            self.texts.get("download_single", "Download Single Video"), 
            QMessageBox.ButtonRole.NoRole
        )
        
        msg.exec()
        
        # Return True if user chose to download playlist
        return msg.clickedButton() == playlist_button
    
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
        if self.is_playlist_url(video_url):
            is_playlist = self.show_playlist_dialog()
        
        # Create and start download thread with playlist option
        self.download_thread = DownloadThread(video_url, format_type, quality, self.texts, is_playlist)
        self.download_thread.status_update.connect(self.update_status)
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
    
    def download_finished(self, success, message):
        """
        Handle download completion, update UI and show result dialog.
        
        Args:
            success (bool): Whether download completed successfully
            message (str): Completion message or error details
        """
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



    def get_texts(self, language):
        """
        Get localized text strings for the specified language.
        
        Args:
            language (str): Language code (English, Deutsch, Español, Français)
            
        Returns:
            dict: Dictionary containing all UI text strings in the specified language
        """
        # Define translations for the UI
        translations = {
            "English": {
                "title": "Video Downloader",
                "app_title": "YouTube Video Downloader",
                "url_label": "Enter Video URL:",
                "format_label": "Select Format:",
                "quality_label": "Select Video Quality:",
                "download_button": "Download",
                "downloading": "Downloading... Please wait.",
                "download_complete": "Download complete!",
                "download_failed": "Download failed.",
                "success": "Success",
                "error": "Error",
                "url_error": "Please enter a video URL.",
                "download_error": "Failed to download the video. Please check the URL or your internet connection.",
                "paste": "Paste",
                "delete": "Delete",
                "playlist_detected": "Playlist Detected",
                "playlist_question": "This appears to be a playlist URL. What would you like to download?",
                "download_playlist": "Download Entire Playlist",
                "download_single": "Download Single Video",
            },
            "Deutsch": {
                "title": "Video-Downloader",
                "app_title": "YouTube Video-Downloader",
                "url_label": "Geben Sie die Video-URL ein:",
                "format_label": "Format auswählen:",
                "quality_label": "Videoqualität auswählen:",
                "download_button": "Herunterladen",
                "downloading": "Herunterladen... Bitte warten.",
                "download_complete": "Download abgeschlossen!",
                "download_failed": "Download fehlgeschlagen.",
                "success": "Erfolg",
                "error": "Fehler",
                "url_error": "Bitte geben Sie eine Video-URL ein.",
                "download_error": "Das Video konnte nicht heruntergeladen werden. Bitte überprüfen Sie die URL oder Ihre Internetverbindung.",
                "paste": "Einfügen",
                "delete": "Löschen",
                "playlist_detected": "Playlist erkannt",
                "playlist_question": "Dies scheint eine Playlist-URL zu sein. Was möchten Sie herunterladen?",
                "download_playlist": "Gesamte Playlist herunterladen",
                "download_single": "Einzelnes Video herunterladen",
            },
            "Español": {
                "title": "Descargador de Videos",
                "app_title": "Descargador de Videos de YouTube",
                "url_label": "Introduce la URL del video:",
                "format_label": "Selecciona el formato:",
                "quality_label": "Selecciona la calidad del video:",
                "download_button": "Descargar",
                "downloading": "Descargando... Por favor espera.",
                "download_complete": "¡Descarga completada!",
                "download_failed": "Descarga fallida.",
                "success": "Éxito",
                "error": "Error",
                "url_error": "Por favor, introduce una URL de video.",
                "download_error": "No se pudo descargar el video. Verifica la URL o tu conexión a internet.",
                "paste": "Insertar",
                "delete": "Eliminar",
                "playlist_detected": "Lista de reproducción detectada",
                "playlist_question": "Parece que es una URL de lista de reproducción. ¿Qué te gustaría descargar?",
                "download_playlist": "Descargar lista completa",
                "download_single": "Descargar video individual",
            },
            "Français": {
                "title": "Téléchargeur de Vidéos",
                "app_title": "Téléchargeur de Vidéos YouTube",
                "url_label": "Entrez l'URL de la vidéo :",
                "format_label": "Choisir le format :",
                "quality_label": "Choisir la qualité vidéo :",
                "download_button": "Télécharger",
                "downloading": "Téléchargement... Veuillez patienter.",
                "download_complete": "Téléchargement terminé !",
                "download_failed": "Échec du téléchargement.",
                "success": "Succès",
                "error": "Erreur",
                "url_error": "Veuillez entrer une URL de vidéo.",
                "download_error": "Impossible de télécharger la vidéo. Vérifiez l'URL ou votre connexion internet.",
                "paste": "Insérer",
                "delete": "Supprimer",
                "playlist_detected": "Playlist détectée",
                "playlist_question": "Ceci semble être une URL de playlist. Que souhaitez-vous télécharger ?",
                "download_playlist": "Télécharger la playlist entière",
                "download_single": "Télécharger une seule vidéo",
            },
        }
        return translations.get(language, translations["English"])

# Application entry point
if __name__ == "__main__":
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
