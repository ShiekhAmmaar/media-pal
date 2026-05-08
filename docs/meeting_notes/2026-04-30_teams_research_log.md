# Comm Log: Dr. Sajjad

**Date:** 2026-04-30
**Topic:** Pre-Kickoff Research Update & Architecture Feedback
**Method:** Email / Microsoft Teams Exchange

## Update Sent to Dr. Sajjad

* **Competitive Analysis:** 
  * Manual filtering services (VidAngel, ClearPlay) rely on hired human reviewers.
  * Algorithmic filtering (Netflix, YouTube) relies on basic metadata and keyword lists, which lacks context and leads to inaccurate blocking.
  * *Our Advantage:* Context-aware, automated AI filtering.

* **Data Model (Kids-in-Mind):** Evaluated their quantitative scoring system (Violence & Gore, Sex & Nudity, Profanity). Proposed taking this further by using AI to automatically cut out flagged parts rather than just providing a review.

* **UI/UX (Common Sense Media):** Identified their parent dashboard as the gold standard target for our user interface.

* **Backend:** Currently researching Claude Agentic setups to execute the filtering.

* **Naming:** Proposed "Media Pal" or "Media Mate".

## Feedback Received from Dr. Sajjad
* **UI Goal:** Agreed that the Common Sense Media dashboard is the closest target for the UI and should be the initial standard to achieve.

* **Parameter Definition:** Instructed to define a strict set of parameters for the model to evaluate (similar to Kids-in-Mind).

* **System Architecture:** Suggested providing the model with the movie name and subtitles, then passing a prompt containing the defined parameters/user profile.

* **Output Template:** Instructed to design a strict output template for the model to follow.

* **Naming & Scope:** Advised keeping the name broad ("Media Pal") for now to avoid limiting the scope. We will evaluate the specific target audience in the future and rename the application accordingly if needed.

* **Action Item:** Instructed to log this message exchange into the project files.