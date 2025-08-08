"""
Format and quality handling for video downloads.

Contains logic for mapping user selections to yt-dlp format strings
and handling different video/audio formats and qualities.
"""


def get_quality_reverse_map():
    """
    Get mapping from localized quality names to standard values.
    
    Returns:
        dict: Mapping of localized quality strings to standard format strings
    """
    return {
        # English
        "Best": "Best", "Lowest": "Lowest",
        # German  
        "Beste": "Best", "Niedrigste": "Lowest",
        # Spanish
        "Mejor": "Best", "Más baja": "Lowest",
        # French
        "Meilleure": "Best", "Plus faible": "Lowest"
    }


def get_format_options(format_type, quality):
    """
    Get yt-dlp format string based on selected format and quality.
    
    Args:
        format_type (str): Format selection - "MP4", "WEBM", "MP3", or "WAV"
        quality (str): Video quality selection (Best, 1080p, etc.) - may be localized
        
    Returns:
        tuple: (format_string, postprocessors_list)
    """
    # Map localized quality to standard format strings
    quality_reverse_map = get_quality_reverse_map()
    standard_quality = quality_reverse_map.get(quality, quality)
    
    # Handle different format types
    if format_type == "MP4":
        quality_formats = {
            "Best": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
            "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]",
            "720p": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]",
            "480p": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]",
            "360p": "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]",
            "Lowest": "worst[ext=mp4]",
        }
        return quality_formats.get(standard_quality, quality_formats["Best"]), []
        
    elif format_type == "WEBM":
        quality_formats = {
            "Best": "bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]",
            "1080p": "bestvideo[height<=1080][ext=webm]+bestaudio[ext=webm]/best[height<=1080][ext=webm]",
            "720p": "bestvideo[height<=720][ext=webm]+bestaudio[ext=webm]/best[height<=720][ext=webm]",
            "480p": "bestvideo[height<=480][ext=webm]+bestaudio[ext=webm]/best[height<=480][ext=webm]",
            "360p": "bestvideo[height<=360][ext=webm]+bestaudio[ext=webm]/best[height<=360][ext=webm]",
            "Lowest": "worst[ext=webm]",
        }
        return quality_formats.get(standard_quality, quality_formats["Best"]), []
        
    elif format_type == "MP3":
        return "bestaudio/best", [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]
        
    elif format_type == "WAV":
        return "bestaudio/best", [{
            'key': 'FFmpegExtractAudio', 
            'preferredcodec': 'wav',
            'preferredquality': '192'
        }]
        
    # Default fallback
    return "best", []