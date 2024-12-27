import tkinter as tk
from tkinter import ttk, messagebox
import subprocess

class VideoDownloaderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Video Downloader")
        self.master.geometry("500x400")
        self.master.resizable(False, False)

        # Title
        title_label = tk.Label(
            self.master, text="YouTube Video Downloader", font=("Arial", 18, "bold")
        )
        title_label.pack(pady=10)

        # URL Entry Field
        url_label = tk.Label(self.master, text="Enter Video URL:", font=("Arial", 12))
        url_label.pack(pady=5)
        
        self.url_entry = ttk.Entry(self.master, width=50, font=("Arial", 10))
        self.url_entry.pack(pady=5)

        # Format Dropdown
        format_label = tk.Label(self.master, text="Select Format:", font=("Arial", 12))
        format_label.pack(pady=5)

        self.format_var = tk.StringVar(value="MP4")
        format_dropdown = ttk.Combobox(
            self.master, textvariable=self.format_var, values=["MP4", "MP3"], state="readonly", font=("Arial", 10)
        )
        format_dropdown.pack(pady=5)

        # Quality Dropdown
        quality_label = tk.Label(self.master, text="Select Video Quality:", font=("Arial", 12))
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
            self.master, text="Download", command=self.download_video
        )
        download_button.pack(pady=20)

        # Status Label
        self.status_label = tk.Label(
            self.master, text="", font=("Arial", 10), fg="green"
        )
        self.status_label.pack()

    def download_video(self):
        video_url = self.url_entry.get().strip()
        format_type = self.format_var.get()
        quality = self.quality_var.get()

        if not video_url:
            messagebox.showerror("Error", "Please enter a video URL.")
            return

        try:
            self.status_label.config(text="Downloading... Please wait.", fg="blue")
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
            self.status_label.config(text="Download complete!", fg="green")
            messagebox.showinfo("Success", "Video downloaded successfully!")
        except subprocess.CalledProcessError:
            self.status_label.config(text="Download failed.", fg="red")
            messagebox.showerror("Error", "Failed to download the video. Please check the URL or your internet connection.")

# Create the application
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()
