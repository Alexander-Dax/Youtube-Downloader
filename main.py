import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading


class LanguageSelectorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Select Language")
        self.master.geometry("300x200")
        self.master.resizable(False, False)

        # Title
        title_label = tk.Label(
            self.master, text="Choose Language", font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)

        # Language Dropdown
        self.language_var = tk.StringVar(value="English")
        language_dropdown = ttk.Combobox(
            self.master,
            textvariable=self.language_var,
            values=["Deutsch", "English", "Español", "Français"],
            state="readonly",
            font=("Arial", 10),
        )
        language_dropdown.pack(pady=20)

        # Proceed Button
        proceed_button = ttk.Button(
            self.master, text="Proceed", command=self.proceed_to_app
        )
        proceed_button.pack(pady=10)

    def proceed_to_app(self):
        selected_language = self.language_var.get()
        self.master.destroy()  # Close the language selection window
        root = tk.Tk()
        VideoDownloaderApp(root, selected_language)
        root.mainloop()


class VideoDownloaderApp:
    def __init__(self, master, language):
        self.master = master
        self.language = language
        self.texts = self.get_texts(language)

        self.master.title(self.texts["title"])
        self.master.geometry("500x400")
        self.master.resizable(False, False)

        # Title
        title_label = tk.Label(
            self.master, text=self.texts["app_title"], font=("Arial", 18, "bold")
        )
        title_label.pack(pady=10)

        # URL Entry Field
        url_label = tk.Label(self.master, text=self.texts["url_label"], font=("Arial", 12))
        url_label.pack(pady=5)

        self.url_entry = ttk.Entry(self.master, width=50, font=("Arial", 10))
        self.url_entry.pack(pady=5)

        # Format Dropdown
        format_label = tk.Label(self.master, text=self.texts["format_label"], font=("Arial", 12))
        format_label.pack(pady=5)

        self.format_var = tk.StringVar(value="MP4")
        format_dropdown = ttk.Combobox(
            self.master, textvariable=self.format_var, values=["MP4", "MP3"], state="readonly", font=("Arial", 10)
        )
        format_dropdown.pack(pady=5)

        # Quality Dropdown
        quality_label = tk.Label(self.master, text=self.texts["quality_label"], font=("Arial", 12))
        quality_label.pack(pady=5)

        self.quality_var = tk.StringVar(value="Best")
        quality_dropdown = ttk.Combobox(
            self.master,
            textvariable=self.quality_var,
            values=["Best", "1080p", "720p", "480p", "360p", "Lowest"],
            state="readonly",
            font=("Arial", 10),
        )
        quality_dropdown.pack(pady=5)

        # Download Button
        download_button = ttk.Button(
            self.master, text=self.texts["download_button"], command=self.start_download_thread
        )
        download_button.pack(pady=20)

        # Status Label
        self.status_label = tk.Label(
            self.master, text="", font=("Arial", 10), fg="green"
        )
        self.status_label.pack()

    def get_texts(self, language):
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
            },
        }
        return translations.get(language, translations["English"])

    def start_download_thread(self):
        # Run the download in a separate thread to keep the GUI responsive
        thread = threading.Thread(target=self.download_video)
        thread.start()

    def download_video(self):
        video_url = self.url_entry.get().strip()
        format_type = self.format_var.get()
        quality = self.quality_var.get()

        if not video_url:
            messagebox.showerror(self.texts["error"], self.texts["url_error"])
            return

        try:
            self.status_label.config(text=self.texts["downloading"], fg="blue")
            self.master.update()

            # Determine yt-dlp options based on user input
            quality_map = {
                "Best": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
                "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]",
                "720p": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]",
                "480p": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]",
                "360p": "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]",
                "Lowest": "worst[ext=mp4]",
            }
            quality_option = quality_map[quality]

            if format_type == "MP4":
                command = f'yt-dlp -f "{quality_option}" -o "%(title)s"-{quality}".%(ext)s" "{video_url}"'
            elif format_type == "MP3":
                command = f'yt-dlp --extract-audio --audio-format mp3 -o "%(title)s.%(ext)s" "{video_url}"'

            # Run yt-dlp command
            subprocess.run(command, shell=True, check=True)
            self.status_label.config(text=self.texts["download_complete"], fg="green")
            messagebox.showinfo(self.texts["success"], self.texts["download_complete"])
        except subprocess.CalledProcessError:
            self.status_label.config(text=self.texts["download_failed"], fg="red")
            messagebox.showerror(self.texts["error"], self.texts["download_error"])


# Start with the language selector
if __name__ == "__main__":
    root = tk.Tk()
    LanguageSelectorApp(root)
    root.mainloop()
