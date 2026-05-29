# Meeting Notes: Dr. Sajjad

**Date:** 2026-05-15
**Topic:** Repository Initialization, Parser Implementation, & Modular LLM Architecture

## Key Discussions

* **Version Control & Repository Setup:**
  * Officially initialized the Git repository for the project at `https://github.com/ShiekhAmmaar/media-pal`.
  * Standardized the project structure by placing all research logs, communications, and tracking records under the `docs/` directory to maintain clean documentation.
  * Agreed to lock in "media-pal" as the working project name. Strategic targeting and final product branding will be revisited once model experimentation yields clear audience demographic insights.

* **Data Ingestion Progress (`parser.py`):**
  * Developed and successfully tested a Python parsing script to clean raw `.srt` movie subtitle files.
  * The cleaning pipeline successfully handles key data optimization steps:
    * Strips out unnecessary HTML formatting tags.
    * Eliminates subtitle index numbers, as they provide no semantic value to the LLM and waste token capacity.
    * Resolves awkward line breaks by joining multi-line subtitles linked to the same timestamp into a single, cohesive text block.
  * Standardized the script's output into a clean JSON array of objects using the following schema:
```json
    {
        "timestamp": "00:00:00,000 --> 00:00:00,000",
        "text": "Cleaned subtitle text block goes here."
    }
    ```
  * Verified the script's efficiency via test runs against multiple movie subtitle datasets; token payloads are optimized and well-formatted for model ingestion.

* **Open-Source LLM R&D Strategy:**
  * Shifting focus toward identifying robust open-source alternatives to Anthropic's Claude to control infrastructure costs and alignment.
  * Actively exploring the **Qwen** model family as a primary candidate. A deep-dive update on its performance parameters will be ready in the coming days.
  * Currently engineering a modular LLM backend execution script. The code is being designed to decouple the specific model API logic from the core pipeline. This will allow the team to swap backend models (e.g., switching API keys or minor initialization parameters) seamlessly without rewriting any downstream analysis code. Target to have the testing suite active by next week.

* **Prompt Engineering & Content Taxonomy:**
  * Initiated the drafting phase for the core system prompts. 
  * Confirmed that the **Kids-In-Mind** scoring taxonomy will serve as our baseline benchmark. System prompts will be heavily tailored to instruct the models to prioritize, classify, and score those specific content vectors (Violence, Profanity, Sex/Nudity).

## Action Items

* [x] Initialize GitHub repository and commit existing project logs under `/docs`.
* [x] Finalize and freeze the baseline `.srt` data parsing pipeline.
* [x] Develop a corresponding parsing script for book formats (`.epub` file ingestion).
* [x] Complete development on the modular LLM backend abstraction script.
* [x] Finalize benchmarking of open-source models (Qwen) against Claude.
* [x] Draft initial iteration of Kids-In-Mind aligned system prompts.