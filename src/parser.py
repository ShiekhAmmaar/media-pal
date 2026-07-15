import re
import json

class MediaParser:
    """Handles ingestion, cleaning, and chunking of subtitle files.""" 
    
    @staticmethod
    def clean_text(text):
        """Removes HTML tags, music notes, and audio cues like [gasps] or (sighs)."""
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\[.*?\]|\(.*?\)', '', text)
        text = text.replace('♪', '')
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
                
                if not cleaned: 
                    continue
                
                if not start_timestamp:
                    start_timestamp = timestamp.split(' --> ')[0]
                
                current_chunk_text.append(cleaned)
                
                if len(current_chunk_text) >= group_size or i == len(blocks) - 1:
                    end_timestamp = timestamp.split(' --> ')[1]
                    grouped_text = " ".join(current_chunk_text)
                    
                    parsed_data.append({
                        "location_flag": f"{start_timestamp} --> {end_timestamp}",
                        "text": grouped_text
                    })
                    
                    current_chunk_text = []
                    start_timestamp = None

        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, indent=4)
        print(f"Success! Condensed into {len(parsed_data)} optimized context chunks.")

# --- RUN THE SCRIPT ---
if __name__ == "__main__":
    parser = MediaParser()
    print("--- Starting Media Pal Ingestion Pipeline ---")
    
    # Change the names to match your downloaded file
    print("\nProcessing Movie Subtitles...")
    parser.parse_srt("data/Deadpool (2016) UHD BluRay 720p, 1080p, . 2160p de Pahe.eng.srt", "data/deadpool_parsed.json", group_size=3)
    
    print("\n--- Pipeline Complete! ---")