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