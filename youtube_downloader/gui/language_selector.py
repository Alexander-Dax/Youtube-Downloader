"""
Language selection dialog for the YouTube Downloader application.

Contains the LanguageSelectorDialog class that allows users to choose
their preferred language for the application interface.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..localization import get_selector_texts


class LanguageSelectorDialog(QDialog):
    """
    Initial dialog window for language selection.
    
    This dialog appears when the application starts, allowing users to choose
    their preferred language for the main application interface. The dialog
    interface updates dynamically based on the selected language.
    """
    
    def __init__(self):
        """Initialize the language selection dialog."""
        super().__init__()
        self.selected_language = "Deutsch"  # Default language
        
        # Create main layout
        layout = QVBoxLayout()
        
        # Title label with bold font
        self.title_label = QLabel()
        self.title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Language dropdown with available languages
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Deutsch", "English", "Español", "Français"])
        self.language_combo.setCurrentText("Deutsch")
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        layout.addWidget(self.language_combo)
        
        # Proceed button to continue to main application
        self.proceed_button = QPushButton()
        self.proceed_button.clicked.connect(self.proceed_to_app)
        layout.addWidget(self.proceed_button)
        
        self.setLayout(layout)
        
        # Initialize with default language
        self.update_interface()
    
    def update_interface(self):
        """Update all interface elements with the currently selected language."""
        current_language = self.language_combo.currentText()
        texts = get_selector_texts(current_language)
        
        # Update window title and labels
        self.setWindowTitle(texts["window_title"])
        self.title_label.setText(texts["title"])
        self.proceed_button.setText(texts["proceed"])
        
        # Adjust window size if needed for longer text
        self.setFixedSize(300, 200)
    
    def on_language_changed(self):
        """Called when user changes language selection in dropdown."""
        self.update_interface()
    
    def proceed_to_app(self):
        """Store selected language and close dialog."""
        self.selected_language = self.language_combo.currentText()
        self.accept()  # Close dialog with accepted status