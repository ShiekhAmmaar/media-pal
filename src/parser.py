import re
import json
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup 

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

def read_file_safely(self, filepath):
    
        """Attempts to read a file using multiple encodings to prevent crashes."""
        
        encodings = ['utf-8', 'latin-1', 'iso-8859-1']
        for enc in encodings:
            try:
                with open(filepath, 'r', encoding=enc) as file:
                    return file.read()
            except UnicodeDecodeError:
                continue
        raise ValueError(f"Could not decode the file: {filepath}")
    
    
def parse_srt(self, srt_file_path, output_json_path, group_size=3):
        """
        Parses subtitles and groups short, rapid dialogue into logical chunks 
        to provide the LLM with better context and save API calls.
        """
        srt_content = self.read_file_safely(srt_file_path)
        blocks = srt_content.strip().split('\n\n')
        
        parsed_data = []
        current_chunk_text = []
        start_timestamp = None
        
        for i, block in enumerate(blocks):
            lines = block.split('\n')
            if len(lines) >= 3:
                timestamp = lines[1].strip()
                raw_text = " ".join(lines[2:])
                cleaned = self.clean_text(raw_text)
                
                # Skip if the audio cue stripper left the line completely empty
                if not cleaned: 
                    continue
                
                # Mark the start timestamp for this group
                if not start_timestamp:
                    start_timestamp = timestamp.split(' --> ')[0]
                
                current_chunk_text.append(cleaned)
                
                # If we hit our group size, or it's the very last block, package it
                if len(current_chunk_text) >= group_size or i == len(blocks) - 1:
                    end_timestamp = timestamp.split(' --> ')[1]
                    grouped_text = " ".join(current_chunk_text)
                    
                    parsed_data.append({
                        "location_flag": f"{start_timestamp} --> {end_timestamp}",
                        "text": grouped_text
                    })
                    
                    # Reset for the next batch
                    current_chunk_text = []
                    start_timestamp = None

        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, indent=4)
        print(f"Success! Condensed into {len(parsed_data)} optimized context chunks.")
        
        
def parse_epub(self, epub_file_path, output_json_path):
    
        """Converts an ebook into JSON array split by paragraphs."""
        try:
            book = epub.read_epub(epub_file_path)
        except Exception as e:
            print(f"Error reading epub: {e}")
            return

        parsed_data = []
        paragraph_index = 1

        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text = soup.get_text(separator='\n')
                paragraphs = [p.strip() for p in text.split('\n') if p.strip()]

                for paragraph in paragraphs:
                    cleaned_paragraph = self.clean_text(paragraph)
                    # Only keep substantial paragraphs to avoid wasting AI tokens on chapter titles
                    if len(cleaned_paragraph) > 20: 
                        parsed_data.append({
                            "location_flag": f"Paragraph {paragraph_index}",
                            "text": cleaned_paragraph
                        })
                        paragraph_index += 1

        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, indent=4)
        print(f"Success! Parsed {len(parsed_data)} book paragraphs.") 

# --- RUN THE SCRIPT ---
if __name__ == "__main__":
    parser = MediaParser()
    
    print("--- Starting Media Pal Ingestion Pipeline ---")
    
    # 1. Test the Subtitle Parser (grouping by 3 lines)
    print("\nProcessing Movie Subtitles...")
    parser.parse_srt("../data/Smurfs2025.srt", "../data/smurfs_parsed.json", group_size=3)
    
    # 2. Test the EPUB Book Parser
    print("\nProcessing EPUB Book...")
    parser.parse_epub("../data/behn-fair-jilt.epub", "../data/behn_parsed.json")
    
    print("\n--- Pipeline Complete! ---")