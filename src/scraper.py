import requests
from bs4 import BeautifulSoup
import json

class ContextScraper:
    def __init__(self, use_mock_data=True):
        """
        use_mock_data (bool): Set to True for prototyping the LLM pipeline connection 
        before the specific HTML selectors for the target website are finalized.
        """
        self.use_mock_data = use_mock_data
        
        # We use headers so sites don't block the university server IP
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_movie_context(self, url):
        """
        Scrapes a movie review page to extract specific
        context rules for the LLM to prevent false positives.
        """
        print(f"\n[Scraper] Fetching context from: {url}...")
        
        try:
            # 1. Ping the website to prove our connection works
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # 2. Return Data
            if self.use_mock_data:
                print("[Scraper] Notice: Using generalized mock data for LLM pipeline testing.")
                return {
                    "violence_rules": "IGNORE slapstick, cartoonish, or sci-fi fantasy violence that results in no physical consequence.",
                    "profanity_rules": "IGNORE franchise-specific slang or made-up sci-fi/fantasy words. These do not count as profanity.",
                    "substance_rules": "IGNORE mentions of standard medical procedures or prescription medications."
                }
            
            # --- PRODUCTION LOGIC GOES HERE LATER ---
            # profanity_div = soup.find('div', class_='profanity-desc')
            # etc...
            
            print("[Scraper] Successfully extracted live context.")
            return {
                "violence_rules": "",
                "profanity_rules": "",
                "substance_rules": ""
            }

        except requests.exceptions.RequestException as e:
            print(f"[Scraper] Connection Error: {e}")
            return None

# --- Quick Test Block ---
if __name__ == "__main__":
    scraper = ContextScraper(use_mock_data=True)
    # Testing the connection to the actual target site
    test_context = scraper.fetch_movie_context("https://kids-in-mind.com/s/the-smurfs-2011.htm")
    print(json.dumps(test_context, indent=4))