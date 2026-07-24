import requests
from bs4 import BeautifulSoup

class ContextScraper:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0'}

    def fetch_movie_context(self, movie_name):
        clean_name = movie_name.lower().replace(" ", "")
        first_letter = clean_name[0] if clean_name else "a"
        url = f"https://kids-in-mind.com/{first_letter}/{clean_name}.htm"
        
        print(f"\n[Scraper] Attempting to fetch real context from: {url}...")
        
        # 1. Establish our baseline safety rules
        context_data = {
            "general_summary": "No specific plot summary available. Grade purely on the provided text.",
            "violence_rules": "IGNORE slapstick, cartoonish, or sci-fi fantasy violence.",
            "profanity_rules": "IGNORE franchise-specific slang.",
            "nudity_rules": "IGNORE innocent, non-sexual partial exposure.",
            "substance_rules": "IGNORE standard medical procedures.",
            "behavioral_rules": "IGNORE standing up to bullies; focus on negative defiance.",
            "thematic_rules": "IGNORE harmless jump scares; focus on intense psychological dread."
        }

        # 2. Try to salvage real-world data
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Scrape all substantial paragraphs to capture the plot and review notes
            paragraphs = soup.find_all('p')
            summary_text = " ".join([p.get_text().strip() for p in paragraphs if len(p.get_text()) > 50])
            
            # Truncate to 1000 characters to save LLM context window/tokens
            if summary_text:
                context_data["general_summary"] = summary_text[:1000] + "..."
                print("[Scraper] Successfully salvaged live contextual data!")
                
        except requests.exceptions.RequestException:
            print(f"[Scraper] Connection failed for {url}. Falling back to baseline rules.")
            
        return context_data 