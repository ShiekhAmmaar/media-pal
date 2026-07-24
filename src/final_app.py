import json
import os
import re
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate

# Import your custom scraper
from scraper import ContextScraper

# --- 1. BUILD THE FEW-SHOT EXAMPLES ---
examples = [
    {
        "subtitle": "Ouch! Darn it, you stepped right on my bad toe!",
        "evaluation": '{"violence": 1, "profanity": 1, "nudity": 0, "substance": 0, "thematic_intensity": 0, "behavioral_modeling": 0, "reasoning": "Extremely mild physical pain and mild substitute profanity."}'
    },
    {
        "subtitle": "He grabbed the interrogator by the throat and slammed his head into the steel table. 'Talk!'",
        "evaluation": '{"violence": 3, "profanity": 0, "nudity": 0, "substance": 0, "thematic_intensity": 3, "behavioral_modeling": 0, "reasoning": "Moderate, realistic physical violence and aggressive interrogation tactics."}'
    },
    {
        "subtitle": "I will gut you like a f***ing pig and watch you bleed out on this floor!",
        "evaluation": '{"violence": 5, "profanity": 5, "nudity": 0, "substance": 0, "thematic_intensity": 4, "behavioral_modeling": 0, "reasoning": "Graphic, extreme threat of lethal violence paired with severe explicit profanity."}'
    },
    {
        "subtitle": "Oh no, the dog stole my towel! Don't look, I'm just in my underwear!",
        "evaluation": '{"violence": 0, "profanity": 0, "nudity": 1, "substance": 0, "thematic_intensity": 0, "behavioral_modeling": 1, "reasoning": "Innocent, comedic partial exposure; slight embarrassment but no sexual context."}'
    },
    {
        "subtitle": "She unbuttoned her blouse, revealing her bra, and pulled him onto the bed. 'Damn, you look good.'",
        "evaluation": '{"violence": 0, "profanity": 2, "nudity": 3, "substance": 0, "thematic_intensity": 0, "behavioral_modeling": 0, "reasoning": "Highly suggestive sexual situation with partial nudity and mild cursing."}'
    },
    {
        "subtitle": "[Explicit sexual moaning] Take it all off. I want to feel every inch of you.",
        "evaluation": '{"violence": 0, "profanity": 0, "nudity": 5, "substance": 0, "thematic_intensity": 0, "behavioral_modeling": 0, "reasoning": "Dialogue and audio cues indicating explicit, graphic sexual intercourse."}'
    },
    {
        "subtitle": "Pour me a glass of champagne, let's celebrate the promotion.",
        "evaluation": '{"violence": 0, "profanity": 0, "nudity": 0, "substance": 1, "thematic_intensity": 0, "behavioral_modeling": 0, "reasoning": "Casual, legal adult consumption of alcohol in a positive context."}'
    },
    {
        "subtitle": "I snagged my older brother's vape. Let's go hit it behind the bleachers so the teachers don't see.",
        "evaluation": '{"violence": 0, "profanity": 0, "nudity": 0, "substance": 3, "thematic_intensity": 0, "behavioral_modeling": 3, "reasoning": "Underage use of restricted substances combined with deceptive, rule-breaking behavior."}'
    },
    {
        "subtitle": "Shut up, mom! You're a b***h! Pass the needle, I need another hit right now.",
        "evaluation": '{"violence": 0, "profanity": 3, "nudity": 0, "substance": 5, "thematic_intensity": 3, "behavioral_modeling": 5, "reasoning": "Hardcore illegal drug addiction, severe verbal abuse, and absolute defiance of a parent."}'
    },
    {
        "subtitle": "[Demonic whispering] I am under your bed. I can see you breathing, but you can't scream.",
        "evaluation": '{"violence": 0, "profanity": 0, "nudity": 0, "substance": 0, "thematic_intensity": 5, "behavioral_modeling": 0, "reasoning": "Maximum psychological dread and terrifying supernatural suspense without a single drop of physical violence."}'
    },
    {
        "subtitle": "I refuse to lie to the principal for you anymore. It's wrong, and I'm telling the truth.",
        "evaluation": '{"violence": 0, "profanity": 0, "nudity": 0, "substance": 0, "thematic_intensity": 0, "behavioral_modeling": 0, "reasoning": "Prosocial behavior; standing up for morality is positive and scores a zero for negative behavioral modeling."}'
    }
]

example_template = """Subtitle: {subtitle}\nOutput: {evaluation}"""
example_prompt = PromptTemplate(
    input_variables=["subtitle", "evaluation"],
    template=example_template
)

# --- 2. CONSTRUCT THE DYNAMIC PROMPT (NO PYDANTIC) ---
prefix = """You are an expert AI content moderator analyzing movie subtitles.

CRITICAL MOVIE CONTEXT (Scraped from trusted sources):
{movie_context}

Assign a severity score from 0 to 5 for Violence, Profanity, Nudity, Substance Use, Thematic Intensity, and Behavioral Modeling.

CRITICAL INSTRUCTION: You must return ONLY a raw, valid JSON object. Do not include any conversational text like "Here is your output".
Do not use markdown blocks. Your keys MUST be exactly: "violence", "profanity", "nudity", "substance", "thematic_intensity", "behavioral_modeling", "reasoning".

Here are some examples of how to score:"""

suffix = """\nNow evaluate the following real subtitle chunk:
Subtitle: {text}
Output:"""

few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix=prefix,
    suffix=suffix,
    input_variables=["text", "movie_context"]
)

# --- 3. ASSEMBLE THE LANGCHAIN PIPELINE ---
llm = ChatOllama(model="llama3.2", base_url="http://localhost:11434", temperature=0)
chain = few_shot_prompt | llm 

# --- 4. EXECUTE BATCH PROCESSING & COMPILATION ---
def run_evaluation(input_file, output_file, movie_title, limit=None):
    if not os.path.exists(input_file):
        print(f"Error: Could not find {input_file}.")
        return {"error": f"Could not find {input_file}"}

    print(f"Scraping context for {movie_title}...")
    scraper = ContextScraper()
    context_data = scraper.fetch_movie_context(movie_title)
    
    if context_data is None:
        context_data = {}
    
    formatted_context = f"""
    - General Movie Tone & Plot: {context_data.get('general_summary', 'None')}
    - Profanity Rules: {context_data.get('profanity_rules', 'None')}
    - Violence Rules: {context_data.get('violence_rules', 'None')}
    - Nudity Rules: {context_data.get('nudity_rules', 'None')}
    - Substance Rules: {context_data.get('substance_rules', 'None')}
    - Behavioral Rules: {context_data.get('behavioral_rules', 'None')}
    - Thematic Rules: {context_data.get('thematic_rules', 'None')}
    """

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    test_batch = data[:limit] if limit else data
    chunk_evaluations = []

    overall_scores = {
        "violence": 0, "profanity": 0, "nudity": 0,
        "substance": 0, "thematic_intensity": 0, "behavioral_modeling": 0
    }

    print(f"Starting pipeline on {len(test_batch)} chunks...")

    for chunk in test_batch:
        print(f"Processing: {chunk['location_flag']}")
        try:
            # 1. Get raw text
            raw_response = chain.invoke({
                "text": chunk['text'],
                "movie_context": formatted_context
            })
            raw_text = raw_response.content
            
            # 2. Bulletproof regex to extract JSON
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if not match:
                raise ValueError(f"No JSON brackets found. LLM said: {raw_text}")
            
            clean_text = match.group(0)
            
            # Clean out any accidental escaped quotes in the keys the LLM might have thrown in
            clean_text = clean_text.replace('"\\"', '"').replace('\\""', '"')
            
            eval_dict = json.loads(clean_text)
            
            # 3. Update peak scores securely (handling if the LLM output a string instead of an int)
            for key in overall_scores.keys():
                val = eval_dict.get(key, 0)
                try:
                    val_int = int(val)
                    overall_scores[key] = max(overall_scores[key], val_int)
                    eval_dict[key] = val_int # Normalize back to int
                except (ValueError, TypeError):
                    pass

            chunk_evaluations.append({
                "timestamp": chunk['location_flag'],
                "original_text": chunk['text'],
                "evaluation": eval_dict
            })
            
        except Exception as e:
            print(f"--- FAILED TO PARSE CHUNK ---")
            print(f"Error: {e}")
            
            # We append a safe fallback dictionary so the GUI never crashes later
            chunk_evaluations.append({
                "timestamp": chunk['location_flag'],
                "original_text": chunk['text'],
                "evaluation": {
                    "violence": 0, "profanity": 0, "nudity": 0, 
                    "substance": 0, "thematic_intensity": 0, 
                    "behavioral_modeling": 0, 
                    "reasoning": f"ERROR PARSING: {str(e)}"
                }
            })

    final_output = {
        "movie_title": movie_title,
        "total_chunks_analyzed": len(test_batch),
        "overall_scores": overall_scores,
        "chunk_evaluations": chunk_evaluations
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=4)
    
    print(f"\nFinished! Results saved to {output_file}")
    return final_output

if __name__ == "__main__":
    IN_PATH = "data/deadpool_parsed.json"
    OUT_PATH = "data/deadpool_final_eval.json"
    TARGET_TITLE = "Deadpool"
    
    # Keeping limit at 5 so you get instant feedback
    run_evaluation(IN_PATH, OUT_PATH, TARGET_TITLE, limit=None)