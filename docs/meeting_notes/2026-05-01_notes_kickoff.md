# Meeting Notes: Dr. Sajjad

**Date:** 2026-05-01
**Topic:** Summer Project Kickoff

## Project Foundation Finalized

* **Project Name Officially Set:** Media Pal (Subject to future audience review).
* **Intervention Architecture (Pivot):** Hard-skipping flagged media parts is considered less user-friendly. The new vision is to put a warning layer/overlay on top of the flagged media (similar to YouTube's copyright issue screens).
* **UI/UX Target:** The system must extract and display the "exact content" (copying the exact subtitles for the video) alongside the AI's explanation of why it was flagged.

## Technical Decisions

* **LLM Engine Benchmarking:**
  * **Upper Bound:** Claude Agent (will require securing a subscription/API access).
  * **Open Source Alternatives:** *Qwen* was identified as a strong potential open-source candidate. Need to research other alternatives to compare against Claude's performance.

* **Data Model Parameters:**
  * Continue utilizing Kids-in-Mind quantitative scoring as a baseline.
  * **New Directive:** Conduct deeper research into Common Sense Media's specific grading parameters to potentially integrate them into our classification model.

* **DevOps:** Initialized the `media-pal` GitHub repository and established a version-controlled documentation system for meeting logs and architecture decisions.

## Action Items (May Sprint)
- [ ] Write Python scripts to parse and copy the exact `.srt` (movie subtitles) into clean JSON data.
- [ ] Secure subscription/API access for the baseline Claude Agent.
- [ ] Research and test Qwen and other open-source LLM alternatives against the Claude benchmark.
- [ ] Research Common Sense Media's specific grading parameters.
- [ ] Draft baseline system prompts to ensure the LLM outputs both the exact flagged content and the contextual explanation.