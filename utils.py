"""
Utility functions for the Automatic Web Scraper
"""

import logging
import re
import time
from urllib.parse import urlparse

def setup_logging(level="INFO"):
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def validate_url(url):
    """
    Validate if the provided URL is properly formatted.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def format_time(seconds):
    """
    Format time in seconds to a human-readable string.
    
    Args:
        seconds (float): Time in seconds
        
    Returns:
        str: Formatted time string
    """
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

def extract_domain(url):
    """
    Extract domain name from URL.
    
    Args:
        url (str): URL to extract domain from
        
    Returns:
        str: Domain name
    """
    try:
        return urlparse(url).netloc
    except:
        return "unknown"

def clean_text(text):
    """
    Clean text by removing extra whitespace and special characters.
    
    Args:
        text (str): Text to clean
        
    Returns:
        str: Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.,!?;:()\-]', '', text)
    return text.strip()

def estimate_reading_time(text, words_per_minute=200):
    """
    Estimate reading time for text.
    
    Args:
        text (str): Text to estimate reading time for
        words_per_minute (int): Average reading speed
        
    Returns:
        str: Estimated reading time
    """
    word_count = len(text.split())
    minutes = word_count / words_per_minute
    
    if minutes < 1:
        return "< 1 minute"
    elif minutes < 60:
        return f"{minutes:.0f} minutes"
    else:
        hours = minutes / 60
        return f"{hours:.1f} hours"
