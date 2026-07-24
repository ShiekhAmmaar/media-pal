import json
import os
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

# Import your custom scraper
from scraper import ContextScraper

# --- 1. DEFINE STRICT OUTPUT STRUCTURE ---
class ModerationScore(BaseModel):
    violence: int = Field(description="Score from 0 to 5 for physical harm or threats")
    profanity: int = Field(description="Score from 0 to 5 for crude or explicit language")
    nudity: int = Field(description="Score from 0 to 5 for nudity or sexual content")
    substance: int = Field(description="Score from 0 to 5 for alcohol, tobacco, or drug use")
    thematic_intensity: int = Field(description="Score from 0 to 5 for suspense, psychological dread, or intense thematic elements")
    behavioral_modeling: int = Field(description="Score from 0 to 5 for disrespect towards authority, defiance, lying, or unpunished bad behavior")
    reasoning: str = Field(description="One short sentence explaining the scores, naming any trigger phrases.")

parser = PydanticOutputParser(pydantic_object=ModerationScore)

# --- 2. BUILD THE FEW-SHOT EXAMPLES ---
examples = [
    {
        # MILD CROSSOVER (Violence 1, Profanity 1)
        "subtitle": "Ouch! Darn it, you stepped right on my bad toe!",
        "evaluation": '{"violence": 1, "profanity": 1, "nudity": 0, "substance": 0, "thematic_intensity": 0, "behavioral_modeling": 0, "reasoning": "Extremely mild physical pain and mild substitute profanity."}'
    },
    {
        # MODERATE CROSSOVER (Violence 3, Thematic 3)
        "subtitle": "He grabbed the interrogator by the throat and slammed his head into the steel table. 'Talk!'",
        "evaluation": '{"violence": 3, "profanity": 0, "nudity": 0, "substance": 0, "thematic_intensity": 3, "behavioral_modeling": 0, "reasoning": "Moderate, realistic physical violence and aggressive interrogation tactics."}'
    },
    {
        # EXTREME CROSSOVER (Violence 5, Profanity 5)
        "subtitle": "I will gut you like a f***ing pig and watch you bleed out on this floor!",
        "evaluation": '{"violence": 5, "profanity": 5, "nudity": 0, "substance": 0, "thematic_intensity": 4, "behavioral_modeling": 0, "reasoning": "Graphic, extreme threat of lethal violence paired with severe explicit profanity."}'
    },
    {
        # MILD NUDITY / COMEDIC (Nudity 1, Behavioral 1)
        "subtitle": "Oh no, the dog stole my towel! Don't look, I'm just in my underwear!",
        "evaluation": '{"violence": 0, "profanity": 0, "nudity": 1, "substance": 0, "thematic_intensity": 0, "behavioral_modeling": 1, "reasoning": "Innocent, comedic partial exposure; slight embarrassment but no sexual context."}'
    },
    {
        # MODERATE NUDITY / SUGGESTIVE (Nudity 3, Profanity 2)
        "subtitle": "She unbuttoned her blouse, revealing her bra, and pulled him onto the bed. 'Damn, you look good.'",
        "evaluation": '{"violence": 0, "profanity": 2, "nudity": 3, "substance": 0, "thematic_intensity": 0, "behavioral_modeling": 0, "reasoning": "Highly suggestive sexual situation with partial nudity and mild cursing."}'
    },
    {
        # EXTREME NUDITY (Nudity 5)
        "subtitle": "[Explicit sexual moaning] Take it all off. I want to feel every inch of you.",
        "evaluation": '{"violence": 0, "profanity": 0, "nudity": 5, "substance": 0, "thematic_intensity": 0, "behavioral_modeling": 0, "reasoning": "Dialogue and audio cues indicating explicit, graphic sexual intercourse."}'
    },
    {
        # MILD SUBSTANCE (Substance 1)
        "subtitle": "Pour me a glass of champagne, let's celebrate the promotion.",
        "evaluation": '{"violence": 0, "profanity": 0, "nudity": 0, "substance": 1, "thematic_intensity": 0, "behavioral_modeling": 0, "reasoning": "Casual, legal adult consumption of alcohol in a positive context."}'
    },
    {
        # MODERATE SUBSTANCE & BEHAVIORAL (Substance 3, Behavioral 3)
        "subtitle": "I snagged my older brother's vape. Let's go hit it behind the bleachers so the teachers don't see.",
        "evaluation": '{"violence": 0, "profanity": 0, "nudity": 0, "substance": 3, "thematic_intensity": 0, "behavioral_modeling": 3, "reasoning": "Underage use of restricted substances combined with deceptive, rule-breaking behavior."}'
    },
    {
        # EXTREME SUBSTANCE & BEHAVIORAL (Substance 5, Behavioral 5, Profanity 3)
        "subtitle": "Shut up, mom! You're a b***h! Pass the needle, I need another hit right now.",
        "evaluation": '{"violence": 0, "profanity": 3, "nudity": 0, "substance": 5, "thematic_intensity": 3, "behavioral_modeling": 5, "reasoning": "Hardcore illegal drug addiction, severe verbal abuse, and absolute defiance of a parent."}'
    },
    {
        # EXTREME THEMATIC INTENSITY (Thematic 5, Violence 0)
        "subtitle": "[Demonic whispering] I am under your bed. I can see you breathing, but you can't scream.",
        "evaluation": '{"violence": 0, "profanity": 0, "nudity": 0, "substance": 0, "thematic_intensity": 5, "behavioral_modeling": 0, "reasoning": "Maximum psychological dread and terrifying supernatural suspense without a single drop of physical violence."}'
    },
    {
        # THE ANTI-EDGE CASE (Zeroing out metrics properly)
        "subtitle": "I refuse to lie to the principal for you anymore. It's wrong, and I'm telling the truth.",
        "evaluation": '{"violence": 0, "profanity": 0, "nudity": 0, "substance": 0, "thematic_intensity": 0, "behavioral_modeling": 0, "reasoning": "Prosocial behavior; standing up for morality is positive and scores a zero for negative behavioral modeling."}'
    }
]

example_template = """Subtitle: {subtitle}\nOutput: {evaluation}"""
example_prompt = PromptTemplate(
    input_variables=["subtitle", "evaluation"],
    template=example_template
)

# --- 3. CONSTRUCT THE DYNAMIC PROMPT ---
prefix = """You are an expert AI content moderator analyzing movie subtitles.

CRITICAL MOVIE CONTEXT (Scraped from trusted sources):
{movie_context}

Assign a severity score from 0 to 5 for Violence, Profanity, Nudity, Substance Use, Thematic Intensity, and Behavioral Modeling.

CRITICAL INSTRUCTION: You must return ONLY a raw, valid JSON object. Do not include any conversational text. Do not wrap the output in markdown code blocks. All JSON keys MUST be strictly lowercase.

{format_instructions}

Here are some examples of how to score:"""

suffix = """\nNow evaluate the following real subtitle chunk:
Subtitle: {text}
Output:"""

few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix=prefix,
    suffix=suffix,
    input_variables=["text", "movie_context"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# --- 4. ASSEMBLE THE LANGCHAIN PIPELINE ---
llm = ChatOllama(model="llama3.2", base_url="http://localhost:11434", temperature=0)
chain = few_shot_prompt | llm

# --- 5. EXECUTE BATCH PROCESSING & COMPILATION ---
def run_evaluation(input_file, output_file, movie_title, limit=None):
    if not os.path.exists(input_file):
        print(f"Error: Could not find {input_file}.")
        return {"error": f"Could not find {input_file}"}

    # Fire up the scraper
    print(f"Scraping context for {movie_title}...")
    scraper = ContextScraper()
    
    # We now pass the movie title directly instead of the URL
    context_data = scraper.fetch_movie_context(movie_title)
    
    if context_data is None:
        context_data = {}
    
    # Inject all the newly scraped fields directly into the LLM context block
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

    # Track overall maximum severity scores across the entire film
    overall_scores = {
        "violence": 0,
        "profanity": 0,
        "nudity": 0,
        "substance": 0,
        "thematic_intensity": 0,
        "behavioral_modeling": 0
    }

    print(f"Starting LangChain pipeline on {len(test_batch)} subtitle chunks...")

    for chunk in test_batch:
        print(f"Processing timestamp: {chunk['location_flag']}")
        try:
            # 1. Get the raw text from the LLM
            raw_response = chain.invoke({
                "text": chunk['text'],
                "movie_context": formatted_context
            })
            raw_text = raw_response.content
            
            # 2. THE NUCLEAR OPTION: Find the exact JSON brackets
            start_idx = raw_text.find('{')
            end_idx = raw_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                # Slice out only the JSON portion
                clean_text = raw_text[start_idx:end_idx+1]
                
                # Parse using standard Python JSON (Bypassing LangChain completely)
                eval_dict = json.loads(clean_text)
            else:
                raise ValueError("No JSON brackets {} found in LLM output.")
            
            # 3. Update peak overall scores
            for key in overall_scores.keys():
                if key in eval_dict and isinstance(eval_dict[key], int):
                    overall_scores[key] = max(overall_scores[key], eval_dict[key])

            chunk_evaluations.append({
                "timestamp": chunk['location_flag'],
                "original_text": chunk['text'],
                "evaluation": eval_dict
            })
            
        except Exception as e:
            print(f"\n--- ERROR ON CHUNK ---")
            print(f"Timestamp: {chunk['location_flag']}")
            print(f"Error Type: {type(e).__name__} - {e}")
            print(f"RAW LLM OUTPUT:\n{raw_text if 'raw_text' in locals() else 'Failed to generate text'}")
            print(f"----------------------\n")
            
            chunk_evaluations.append({
                "timestamp": chunk['location_flag'],
                "original_text": chunk['text'],
                "evaluation": {"error": "Failed to parse JSON output", "details": str(e)}
            })
            
    # Compile into a master output structure
    final_output = {
        "movie_title": movie_title,
        "total_chunks_analyzed": len(test_batch),
        "overall_scores": overall_scores,
        "chunk_evaluations": chunk_evaluations
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=4)
    
    print(f"\nFinished! Results compiled and saved to {output_file}")
    return final_output

if __name__ == "__main__":
    IN_PATH = "data/deadpool_parsed.json"
    OUT_PATH = "data/deadpool_final_eval.json"
    TARGET_TITLE = "Deadpool"
    
    run_evaluation(IN_PATH, OUT_PATH, TARGET_TITLE, limit=None)