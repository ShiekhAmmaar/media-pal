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
    violence: int = Field(description="Score from 0 to 5 for violence")
    profanity: int = Field(description="Score from 0 to 5 for profanity")
    nudity: int = Field(description="Score from 0 to 5 for nudity/sexual content")
    substance: int = Field(description="Score from 0 to 5 for substance use")
    thematic_intensity: int = Field(description="Score from 0 to 5 for suspense, psychological dread, or intense/frightening thematic elements")
    reasoning: str = Field(description="One short sentence explaining the scores, naming the trigger phrase.")

parser = PydanticOutputParser(pydantic_object=ModerationScore)

# --- 2. BUILD THE FEW-SHOT EXAMPLES ---
# These "golden examples" teach the LLM exactly how to grade edge cases
examples = [
    {
        # Edge Case: Franchise-specific slang that sounds like profanity
        "subtitle": "What the Smurf are you doing here?",
        "evaluation": '{"violence": 0, "profanity": 0, "nudity": 0, "substance": 0, "reasoning": "Uses franchise-specific slang \'Smurf\' which is not profanity."}'
    },
    {
        # Edge Case: Anatomical terms used in a medical or non-sexual context
        "subtitle": "The doctor says you broke your breastbone and need a cast.",
        "evaluation": '{"violence": 2, "profanity": 0, "nudity": 0, "substance": 0, "reasoning": "Medical discussion of an injury; \'breastbone\' is not sexual nudity."}'
    },
    {
        # Edge Case: Slapstick/Cartoon violence vs. Realistic violence
        "subtitle": "He slipped on the banana peel and bonked his head on the anvil!",
        "evaluation": '{"violence": 1, "profanity": 0, "nudity": 0, "substance": 0, "reasoning": "Mild slapstick/cartoon violence with no severe physical trauma."}'
    },
    {
        # Edge Case: Casual implied substance use vs. Abuse
        "subtitle": "I need a drink after the day I've had. Barkeep, hit me.",
        "evaluation": '{"violence": 0, "profanity": 0, "nudity": 0, "substance": 1, "reasoning": "Casual implied request for alcohol, no illegal drugs or addiction themes."}'
    },
    {
        # Edge Case: Extreme explicit violation (The Anchor)
        "subtitle": "I'm going to rip your head off, you stupid idiot!",
        "evaluation": '{"violence": 4, "profanity": 2, "nudity": 0, "substance": 0, "reasoning": "Explicit threat of physical harm and mild insults."}'
    },
    {
        # Edge Case: Hyperbole / Common Idioms (Often misflagged as extreme violence)
        "subtitle": "If I have to sit through another boring lecture, I'm going to shoot myself.",
        "evaluation": '{"violence": 0, "profanity": 0, "nudity": 0, "substance": 0, "reasoning": "Common hyperbolic idiom expressing boredom; no actual threat of violence."}'
    },
    {
        # Edge Case: Innocent/Non-Sexual Nudity
        "subtitle": "We need to get the baby in the bath, he's running around bare-bottomed!",
        "evaluation": '{"violence": 0, "profanity": 0, "nudity": 0, "substance": 0, "reasoning": "Innocent, non-sexual mention of a baby bathing."}'
    },
    {
        # Edge Case: Sci-Fi/Fantasy Destruction (No biological harm)
        "subtitle": "The star cruiser fired its laser cannons, obliterating the asteroid into dust.",
        "evaluation": '{"violence": 1, "profanity": 0, "nudity": 0, "substance": 0, "reasoning": "Fantasy/Sci-fi action directed at an inanimate object with no biological harm."}'
    },
    {
        # Edge Case: Standard Medical/Prescription Drugs (Often misflagged as illegal substance abuse)
        "subtitle": "It's time for your medication. Did you take your insulin today?",
        "evaluation": '{"violence": 0, "profanity": 0, "nudity": 0, "substance": 1, "reasoning": "Standard mention of legal medical drugs; no intoxication or abuse themes."}'
    },
    {
        # Edge Case: Positive/Empathetic use of Profanity
        "subtitle": "That was a brilliant shot, I'm so damn proud of you!",
        "evaluation": '{"violence": 0, "profanity": 2, "nudity": 0, "substance": 0, "reasoning": "Mild crude language used in a positive, congratulatory context."}'
    },
    {
        # Edge Case: Pure suspense/psychological dread without any physical violence
        "subtitle": "It's in the house. Hide under the bed and don't make a single sound.",
        "evaluation": '{"violence": 0, "profanity": 0, "nudity": 0, "substance": 0, "thematic_intensity": 4, "crude_humor": 0, "reasoning": "High suspense and implied threat causing psychological dread, but no physical violence actually occurs."}'
    },
    {
        # Edge Case: Slapstick/cartoonish "scares" that shouldn't trigger high intensity
        "subtitle": "Boo! Haha, I got you! You should have seen the look on your face!",
        "evaluation": '{"violence": 0, "profanity": 0, "nudity": 0, "substance": 0, "thematic_intensity": 1, "crude_humor": 0, "reasoning": "Playful, harmless jump scare among friends."}'
    },
    {
        # Edge Case: Medical/clinical bodily functions that shouldn't trigger crude humor
        "subtitle": "The patient is experiencing severe nausea and flatulence after the surgery.",
        "evaluation": '{"violence": 0, "profanity": 0, "nudity": 0, "substance": 0, "thematic_intensity": 0, "crude_humor": 0, "reasoning": "Clinical, non-comedic discussion of bodily functions in a medical setting."}'
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

Assign a severity score from 0 to 5 for Violence, Profanity, Nudity, and Substance Use, keeping the above context in mind.

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
# Temperature is 0 so the model is analytical, not creative
llm = ChatOllama(model="llama3.2", base_url="http://localhost:11434", temperature=0)
chain = few_shot_prompt | llm | parser

# --- 5. EXECUTE THE BATCH PROCESSING ---
def run_evaluation(input_file, output_file, movie_title, movie_url, limit=5):
    if not os.path.exists(input_file):
        print(f"Error: Could not find {input_file}. Make sure you are running this from the main media-pal folder.")
        return

    # Fire up the scraper
    print(f"Scraping context for {movie_title}...")
    scraper = ContextScraper()
    context_data = scraper.fetch_movie_context(movie_url)
    
    # If scraper fails and returns None, default to an empty dictionary
    if context_data is None:
        context_data = {}
    
    # Format the scraped dictionary into a readable string
    formatted_context = f"""
    - Profanity Rules: {context_data.get('profanity_rules', 'None')}
    - Violence Rules: {context_data.get('violence_rules', 'None')}
    - Substance Rules: {context_data.get('substance_rules', 'None')}
    """

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    test_batch = data[:limit]
    results = []

    print(f"Starting LangChain pipeline on {len(test_batch)} subtitle chunks...")

    for chunk in test_batch:
        print(f"Processing timestamp: {chunk['location_flag']}")
        try:
            # Pass both the text AND the scraped context into the chain
            result = chain.invoke({
                "text": chunk['text'],
                "movie_context": formatted_context
            })
            
            results.append({
                "timestamp": chunk['location_flag'],
                "original_text": chunk['text'],
                "evaluation": result.model_dump() # Pydantic converts the output back to a clean dictionary
            })
        except Exception as e:
            print(f"Error processing chunk: {e}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
    
    print(f"\nFinished! Results saved to {output_file}")

if __name__ == "__main__":
    # 1. Point to your newly parsed full-movie JSON files
    IN_PATH = "data/deadpool_parsed.json"
    OUT_PATH = "data/deadpool_final_eval.json"
    
    # 2. Update the movie details for the scraper to grab correct context rules
    TARGET_TITLE = "Deadpool"
    TARGET_URL = "[https://kids-in-mind.com/d/deadpool.htm](https://kids-in-mind.com/d/deadpool.htm)"
    
    # 3. Set limit to None to process the entire movie on the Calvert GPUs
    run_evaluation(IN_PATH, OUT_PATH, TARGET_TITLE, TARGET_URL, limit=None) 