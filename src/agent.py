import os
import json
import time
import re
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

class MediaPalAgent:
    """Handles the communication between our parsed data and the Hugging Face Qwen model."""
    
    def __init__(self):
        load_dotenv()
        token = os.getenv("HF_TOKEN")
        
        if token and token != "hf_your_actual_token_goes_here":
            self.client = InferenceClient(api_key=token)
            self.is_active = True
        else:
            self.client = None
            self.is_active = False
            print("WARNING: No valid HF_TOKEN found. Engine running in Mock Mode.")
            
    def get_system_prompt(self):
        """The strict rulebook for the AI."""
        return """
        You are the Media Pal AI, a strict context-aware content classification agent.
        Evaluate the provided movie subtitle text for appropriateness.
        
        Score the following parameters on a scale of 0 to 5 (0 = completely safe, 5 = severe):
        1. Violence
        2. Profanity
        3. Nudity/Sexual Content
        4. Substance Use
        
        You must return ONLY a raw JSON object. Do not include markdown, code blocks, or conversational text.
        Format:
        {
            "scores": {"violence": int, "profanity": int, "nudity": int, "substance": int},
            "reasoning": "One short sentence explaining the scores."
        }
        """

    def extract_json(self, raw_text):
        """
        Open-source models often stubbornly wrap JSON in markdown (```json ... ```).
        This regex safely extracts just the dictionary bracket payload.
        """
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            return match.group(0)
        return raw_text
    
    def analyze_chunk(self, text_chunk):
        """Sends a single group of subtitles to Qwen via Hugging Face."""
        if not self.is_active:
            return {"error": "Mock mode - HF_TOKEN required for real analysis."}

        try:
            # Pinging the free Serverless Inference API for Qwen
            response = self.client.chat_completion(
                model="Qwen/Qwen2.5-72B-Instruct",
                messages=[
                    {"role": "system", "content": self.get_system_prompt()},
                    {"role": "user", "content": f"Analyze this subtitle chunk: {text_chunk}"}
                ],
                max_tokens=200,
                temperature=0.1 # Very low temperature for highly predictable JSON formatting
            )
            
            raw_output = response.choices[0].message.content
            clean_json_string = self.extract_json(raw_output)
            
            return json.loads(clean_json_string)
            
        except Exception as e:
            print(f"API Error: {e}")
            return {"error": "Failed to analyze chunk"}
        
def run_evaluation_pipeline(input_file, output_file, test_limit=5):
    """Loads parsed data, runs it through the Qwen Agent, and saves the results."""
    
    agent = MediaPalAgent()
    
    with open(input_file, 'r', encoding='utf-8') as f:
        parsed_subtitles = json.load(f)

    test_batch = parsed_subtitles[:test_limit]
    evaluated_data = []

    print(f"--- Booting Media Pal Qwen Engine ---")
    print(f"Analyzing {test_limit} chunks...\n")

    for chunk in test_batch:
        print(f"Evaluating timestamp: {chunk['location_flag']}")
        
        analysis = agent.analyze_chunk(chunk['text'])
        
        evaluated_data.append({
            "location_flag": chunk['location_flag'],
            "original_text": chunk['text'],
            "ai_evaluation": analysis
        })
        
        # Hugging Face free tier has rate limits, sleep ensures we don't get blocked
        time.sleep(2)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(evaluated_data, f, indent=4)
        
    print(f"\nSuccess! Evaluations saved to {output_file}")

# --- RUN THE SCRIPT ---
if __name__ == "__main__":
    input_path = "../data/smurfs_parsed.json"
    output_path = "../data/smurfs_evaluated_qwen.json"
    
    run_evaluation_pipeline(input_path, output_path, test_limit=5)