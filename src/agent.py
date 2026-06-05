from scraper import ContextScraper
import json
import requests

class MediaPalAgent:
    """Handles the communication between our parsed data and the local Ollama LLaMA model."""
    
    def __init__(self):
        # No API tokens, no .env file, no mock mode. Just a straight connection to localhost.
        self.endpoint = "http://localhost:11434/api/generate"
        self.model = "llama3.2" 
            
    def get_system_prompt(self, movie_context=None):
        base_prompt = """You are an expert AI content moderator analyzing movie subtitles.
    Evaluate the provided text chunk and assign a severity score from 0 to 5 for the following categories:

    1. VIOLENCE:
    - 0: None.
    - 1-2: Mild, slapstick, or fantasy violence.
    - 3-4 (Moderate/Implied Harm): Descriptions of physical fights, weapons, injuries, or non-graphic death.
    - 5 (Severe/Graphic): Explicit descriptions of blood, gore, torture, or severe physical trauma.

    2. PROFANITY:
    - 0: None.
    - 1-2: Mild insults or crude language (e.g., "hell", "damn", "idiot").
    - 3-4: Moderate expletives (e.g., "bitch", "asshole").
    - 5: Severe/Frequent explicit expletives (e.g., "fuck").

    3. NUDITY/SEXUAL CONTENT:
    - 0: None.
    - 1-2: Mild romantic innuendo, flirting, or anatomical text context.
    - 3-5: Increasing levels of explicit sexual dialogue or descriptions.

    4. SUBSTANCE USE:
    - 0: None.
    - 1-2: Casual mentions of alcohol, smoking, or standard medical drugs.
    - 3-5: Mentions of illegal drug abuse, intoxication, or addiction themes."""

        # --- DYNAMIC CONTEXT INJECTION ---
        context_injection = ""
        if movie_context:
            context_injection = f"""\n\nCRITICAL CONTEXT EXCEPTIONS FOR THIS SPECIFIC TITLE:
    You must strictly apply these rules and ignore flagged words if they fall under these exceptions:
    - Profanity Exceptions: {movie_context.get('profanity_rules', 'None')}
    - Violence Exceptions: {movie_context.get('violence_rules', 'None')}
    - Substance Exceptions: {movie_context.get('substance_rules', 'None')}"""

        # --- STRICT OUTPUT FORMATTING ---
        json_instructions = """\n\nYou must return ONLY a raw JSON object. Do not include markdown, code blocks, or conversational text.
    Format:
    {
        "scores": {"violence": int, "profanity": int, "nudity": int, "substance": int},
        "reasoning": "One short sentence explaining the score, explicitly naming the trigger phrase."
    }"""

        return base_prompt + context_injection + json_instructions

    def analyze_chunk(self, text_chunk):
        """Sends a single group of subtitles to local LLaMA via Ollama."""
        try:
            # Payload pointing to local Ollama API
            payload = {
                "model": self.model,
                "prompt": f"System Guidelines:\n{self.get_system_prompt()}\n\nAnalyze this subtitle chunk: {text_chunk}",
                "stream": False,
                "format": "json" # Ollama's native JSON enforcement
            }
            
            # Pinging the local instance
            response = requests.post(self.endpoint, json=payload)
            response.raise_for_status() # Throws an error if Ollama isn't running
            
            # Extract the string response and load directly into a dictionary
            raw_output = response.json().get("response", "{}")
            return json.loads(raw_output)
            
        except requests.exceptions.RequestException as e:
            print(f"Connection Error: Is Ollama running in your terminal? {e}")
            return {"error": "Failed to connect to local host"}
        except json.JSONDecodeError:
            print(f"JSON Error: Model failed to format correctly. Raw output: {raw_output}")
            return {"error": "Invalid JSON returned"}
        
def run_evaluation_pipeline(input_file, output_file, test_limit=5):
    """Loads parsed data, runs it through the local Agent, and saves the results."""
    
    agent = MediaPalAgent()
    
    with open(input_file, 'r', encoding='utf-8') as f:
        parsed_subtitles = json.load(f)

    test_batch = parsed_subtitles[:test_limit]
    evaluated_data = []

    print(f"--- Booting Media Pal Local LLaMA Engine ---")
    print(f"Analyzing {test_limit} chunks...\n")

    for chunk in test_batch:
        print(f"Evaluating timestamp: {chunk['location_flag']}")
        
        analysis = agent.analyze_chunk(chunk['text'])
        
        evaluated_data.append({
            "location_flag": chunk['location_flag'],
            "original_text": chunk['text'],
            "ai_evaluation": analysis
        })
        
        # The time.sleep(2) has been DELETED. Processing will happen at maximum hardware speed.

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(evaluated_data, f, indent=4)
        
    print(f"\nSuccess! Evaluations saved to {output_file}")

# --- RUN THE SCRIPT ---
if __name__ == "__main__":
    input_path = "../data/smurfs_parsed.json"
    output_path = "../data/smurfs_evaluated_llama3.2.json" # Updated to reflect the model change
    
    # Once you verify this works, bump test_limit to 500 to test the true speed of local inference!
    run_evaluation_pipeline(input_path, output_path, test_limit=100)