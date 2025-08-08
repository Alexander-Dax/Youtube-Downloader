"""
URL utility functions for YouTube link processing.

Contains functions for validating and analyzing YouTube URLs, including
playlist detection and URL pattern matching.
"""

import re


def is_playlist_url(url):
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