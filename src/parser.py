import re
import json
import os

class MediaParser:
    """Handles ingestion, cleaning, and chunking of media files.""" 
    
def clean_text(text):
    
    """Removes HTML tags, music notes, and audio cues like [gasps] or (sighs)."""
    
    #Strip HTML tags like <i>
    text = re.sub(r'<[^>]+>', '', text)
    
    #Strip anything inside brackets or parentheses
    text = re.sub(r'\[.*?\]|\(.*?\)', '', text)
    
    #Strip music notes
    text = text.replace('♪', '')
    
    #Clean up weird spacing left behind
    return " ".join(text.split()).strip()
