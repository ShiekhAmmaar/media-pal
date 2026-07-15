from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate

# 1. Initialize the local LLaMA model via LangChain
llm = ChatOllama(model="llama3.2", base_url="http://localhost:11434")

# 2. Create the Prompt Template
template = """You are an expert AI content moderator. 
Evaluate the following movie subtitle chunk for violence and profanity. 
Keep your reasoning to one short sentence.

Subtitle Chunk: {text}
"""
prompt = PromptTemplate.from_template(template)

# 3. Build the LangChain pipeline
chain = prompt | llm

# --- RUN THE TEST ---
if __name__ == "__main__":
    print("--- Booting LangChain Engine ---")
    test_subtitle = "I'm going to kick your butt, you stupid Smurf!"
    
    # Invoke the chain with our test data
    response = chain.invoke({"text": test_subtitle})
    
    print("\n[AI EVALUATION]:")
    print(response.content)