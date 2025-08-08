"""
Translation strings for all supported languages.

Contains localized text for the GUI interface in English, German, Spanish, and French.
"""


def get_selector_texts(language):
    """
    Get localized text strings for the language selector dialog.
    
    Args:
        language (str): Selected language
        
    Returns:
        dict: Localized text strings for the dialog
    """
    texts = {
        "English": {
            "window_title": "Select Language",
            "title": "Choose Language",
            "proceed": "Proceed"
        },
        "Deutsch": {
            "window_title": "Sprache wählen",
            "title": "Sprache wählen",
            "proceed": "Weiter"
        },
        "Español": {
            "window_title": "Seleccionar idioma",
            "title": "Elegir idioma",
            "proceed": "Continuar"
        },
        "Français": {
            "window_title": "Sélectionner la langue",
            "title": "Choisir la langue",
            "proceed": "Continuer"
        }
    }
    return texts.get(language, texts["English"])


def get_texts(language):
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
            "downloading_button": "Downloading...",
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
            "quality_best": "Best",
            "quality_lowest": "Lowest",
            "destination_label": "Download Destination:",
            "browse_button": "Browse...",
            "select_destination": "Select Download Folder",
            "audio_quality_high": "High Quality",
            "audio_quality_medium": "Medium Quality", 
            "audio_quality_low": "Low Quality",
        },
        "Deutsch": {
            "title": "Video-Downloader",
            "app_title": "YouTube Video-Downloader",
            "url_label": "Geben Sie die Video-URL ein:",
            "format_label": "Format auswählen:",
            "quality_label": "Videoqualität auswählen:",
            "download_button": "Herunterladen",
            "downloading_button": "Herunterladen...",
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
            "quality_best": "Beste",
            "quality_lowest": "Niedrigste",
            "destination_label": "Download-Ordner:",
            "browse_button": "Durchsuchen...",
            "select_destination": "Download-Ordner wählen",
            "audio_quality_high": "Hohe Qualität",
            "audio_quality_medium": "Mittlere Qualität",
            "audio_quality_low": "Niedrige Qualität",
        },
        "Español": {
            "title": "Descargador de Videos",
            "app_title": "Descargador de Videos de YouTube",
            "url_label": "Introduce la URL del video:",
            "format_label": "Selecciona el formato:",
            "quality_label": "Selecciona la calidad del video:",
            "download_button": "Descargar",
            "downloading_button": "Descargando...",
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
            "quality_best": "Mejor",
            "quality_lowest": "Más baja",
            "destination_label": "Carpeta de descarga:",
            "browse_button": "Examinar...",
            "select_destination": "Seleccionar carpeta de descarga",
            "audio_quality_high": "Alta calidad",
            "audio_quality_medium": "Calidad media",
            "audio_quality_low": "Baja calidad",
        },
        "Français": {
            "title": "Téléchargeur de Vidéos",
            "app_title": "Téléchargeur de Vidéos YouTube",
            "url_label": "Entrez l'URL de la vidéo :",
            "format_label": "Choisir le format :",
            "quality_label": "Choisir la qualité vidéo :",
            "download_button": "Télécharger",
            "downloading_button": "Téléchargement...",
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
            "quality_best": "Meilleure",
            "quality_lowest": "Plus faible",
            "destination_label": "Dossier de téléchargement:",
            "browse_button": "Parcourir...",
            "select_destination": "Sélectionner le dossier de téléchargement",
            "audio_quality_high": "Haute qualité",
            "audio_quality_medium": "Qualité moyenne",
            "audio_quality_low": "Basse qualité",
        },
    }
    return translations.get(language, translations["English"])