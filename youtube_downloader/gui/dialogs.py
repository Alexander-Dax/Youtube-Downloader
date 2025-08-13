"""
Dialog windows for the YouTube Downloader application.

Contains various dialog functions and classes for user interactions,
including playlist selection and other confirmation dialogs.
"""

from PyQt6.QtWidgets import QMessageBox


def show_playlist_dialog(parent, texts):
    """
    Show dialog asking user whether to download playlist or single video.
    
    Args:
        parent: Parent widget for the dialog
        texts (dict): Localized text strings
        
    Returns:
        bool: True if user wants to download full playlist, False for single video
    """
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Question)
    msg.setWindowTitle(texts.get("playlist_detected", "Playlist Detected"))
    msg.setText(texts.get("playlist_question", 
               "This appears to be a playlist URL. What would you like to download?"))
    
    # Add custom buttons
    playlist_button = msg.addButton(
        texts.get("download_playlist", "Download Entire Playlist"), 
        QMessageBox.ButtonRole.YesRole
    )
    single_button = msg.addButton(
        texts.get("download_single", "Download Single Video"), 
        QMessageBox.ButtonRole.NoRole
    )
    
    msg.exec()
    
    # Return True if user chose to download playlist
    return msg.clickedButton() == playlist_button