import re
import json
import os

def clean_html_tags(text):
    
    """Removes HTML tags like <i> or <font> from subtitles."""
    clean_text = re.sub(r'<[^>]+>', '', text)
    return clean_text.strip()

def parse_srt_to_json(srt_file_path, output_json_path):
    
    """Reads an .srt file, parses blocks, and saves as JSON."""
    with open(srt_file_path, 'r', encoding='utf-8') as file:
        srt_content = file.read()

    # Split the file by double line breaks (which separates subtitle blocks)
    blocks = srt_content.strip().split('\n\n')
    
    parsed_data = []

    for block in blocks:
        lines = block.split('\n')
        
        if len(lines) >= 3:
            # Line 1 is the index (we don't need it for the AI)
            # Line 2 is the timestamp
            timestamp = lines[1].strip()
            
            # Line 3 and onwards is the text. Join them into one string.
            raw_text = " ".join(lines[2:])
            
            # Clean out the HTML tags
            clean_text = clean_html_tags(raw_text)
            
            # Create the JSON structure Dr. Sajjad wants
            subtitle_object = {
                "timestamp": timestamp,
                "text": clean_text
            }
            
            parsed_data.append(subtitle_object)

    # Save the Python dictionary out as a .json file
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(parsed_data, json_file, indent=4)
        
    print(f"Successfully parsed {len(parsed_data)} subtitle blocks.")
    print(f"Saved to: {output_json_path}")
    
    

# --- RUN ---
if __name__ == "__main__":
    # Define our input and output paths based on our GitHub repo structure
    input_file = ""
    output_file = ""
    
    # Run the parser
    parse_srt_to_json(input_file, output_file)