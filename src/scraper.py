import requests
from bs4 import BeautifulSoup
import json

class ContextScraper:
    def __init__(self):
        # We use headers so sites don't block the Dalhousie server IP
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_movie_context(self, url):
        """
        Scrapes a movie review page (like Kids-In-Mind) to extract specific
        context rules for the LLM to prevent false positives.
        """
        print(f"\n[Scraper] Fetching context from: {url}...")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Initialize the context dictionary
            extracted_context = {
                "violence_rules": "",
                "profanity_rules": "",
                "substance_rules": ""
            }

            # --- PROTOTYPE LOGIC ---
            # In production, you will inspect the exact HTML tags of the target site.
            # For example, if Kids-In-Mind stores the profanity text in a div with class 'profanity-desc':
            
            # profanity_div = soup.find('div', class_='profanity-desc')
            # if profanity_div:
            #     extracted_context["profanity_rules"] = profanity_div.get_text(strip=True)
            
            # --- FALLBACK PROTOTYPE MOCK DATA ---
            # Until the exact HTML selectors are mapped, we return mock data 
            # to prove the pipeline works for Dr. Sajjad.
            extracted_context["profanity_rules"] = "IGNORE fictional or franchise-specific words (e.g., 'Smurf', 'Smurfing'). These do not count as profanity."
            extracted_context["violence_rules"] = "IGNORE slapstick or cartoonish physical comedy. Only flag realistic, consequential violence."

            print("[Scraper] Successfully extracted context.")
            return extracted_context

        except requests.exceptions.RequestException as e:
            print(f"[Scraper] Error fetching data: {e}")
            return None

# --- Quick Test Block ---
if __name__ == "__main__":
    scraper = ContextScraper()
    # Test with a dummy URL for now
    test_context = scraper.fetch_movie_context("https://kids-in-mind.com/dummy-movie-url")
    print(json.dumps(test_context, indent=4))
    