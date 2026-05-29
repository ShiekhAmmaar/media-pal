# Meeting Notes: Dr. Sajjad

**Date:** 2026-05-22
**Topic:** LLM Engine Bottlenecks, Server Migration, & Multimodal Vision Strategy

## Key Discussions

* **The "Blindspot" Pivot (Multimodal Shift):**
  * Evaluated the initial prototype results from the Qwen API trial runs. 
  * Identified a critical conceptual limitation: relying purely on textual context (`.srt` files) results in missed flags for explicit visual scenes with zero dialogue, as well as false positives for aggressive narration/thematic exposition where no physical violence occurs on screen.
  * **Strategic Decision:** Textual context alone is insufficient for a production-ready system. The architecture will pivot to a multimodal approach, processing the video stream itself alongside the text using a Vision LLM to guarantee accurate, context-aware filtering.

* **Model & Infrastructure Overhaul (Ollama & Dal Servers):**
  * Reviewed the performance bottleneck of the free cloud inference tier, which scales to roughly 45 minutes per feature film due to mandatory rate-limiting constraints (`time.sleep(2)`).
  * **Strategic Decision:** To support the heavy compute required for upcoming video frame analysis and bypass external cloud API bottlenecks, the project is abandoning the Hugging Face serverless tier. 
  * The architecture will migrate to running the **LLaMA** model family locally using **Ollama**, hosted on high-compute **Dalhousie University (Dal) servers** to allow for rapid, unthrottled local inference.

* **Security & DevSecOps Intervention:**
  * Reviewed an automated GitHub secret-scanning push protection trigger caused by an accidentally hardcoded API token during testing.
  * Successfully resolved the issue by sanitizing `src/agent.py`, migrating the active authentication keys exclusively into a hidden `.env` file, and executing a `git reset --soft` to purge the exposed token from the local Git history before re-committing.

## Action Items

* [ ] **Server & Ollama Provisioning:** Secure administrative access to the designated Dal servers, install Ollama, and pull the required LLaMA models.
* [ ] **Model Migration:** Refactor the modular backend script to transition from the Hugging Face Qwen API to a local Ollama API endpoint invocation.
* [ ] **Video Processing R&D:** Research and implement Python computer vision libraries (e.g., OpenCV, FFmpeg) to extract key frames from video files for Vision LLM ingestion.
* [ ] **Frontend Integration:** Scaffold the core Chrome Extension (Manifest V3 architecture and content monitoring scripts) to prepare for integration with the incoming metadata maps.