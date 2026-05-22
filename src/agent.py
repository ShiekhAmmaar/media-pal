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