# Weekly Product Review Pulse — Edge Cases & Corner Cases

This document outlines potential edge cases, corner cases, and failure modes for the Weekly Product Review Pulse system, along with suggested mitigation strategies.

---

## 1. Data Ingestion (Scraping & Retrieval)

*   **1.1 Scraper Blocking & Rate Limiting**
    *   *Scenario*: Google Play or App Store temporarily bans the IP or throws a CAPTCHA due to the volume of requests.
    *   *Mitigation*: Implement exponential backoff, user-agent rotation, and potentially use lightweight proxy services if scraping at a high frequency.
*   **1.2 Unpredictable API Schema Changes**
    *   *Scenario*: The underlying DOM or undocumented endpoints used by `google-play-scraper` change overnight, breaking ingestion.
    *   *Mitigation*: Wrap ingestion logic in strong `try-except` blocks. If extraction yields 0 results for a known active app, trigger an immediate developer alert rather than continuing the pipeline.
*   **1.3 Extreme Volume Spikes (Viral Bugs)**
    *   *Scenario*: A breaking bug causes 100x the normal review volume in a single week.
    *   *Mitigation*: Implement a hard cap on the number of reviews processed (e.g., sample the top 5,000 "most helpful" or longest reviews) to prevent memory exhaustion and blown LLM token budgets.
*   **1.4 Extremely Low or Zero Volume**
    *   *Scenario*: A product receives only 2 text-based reviews in an 8-week window.
    *   *Mitigation*: Skip clustering entirely if `len(reviews) < MIN_THRESHOLD`. Directly pass the raw reviews to the LLM for summarization, or skip the run entirely with a simple email stating "Insufficient data for a pulse report."
*   **1.5 Non-English or Emoji-Only Reviews**
    *   *Scenario*: Users leave reviews entirely in Hindi, Spanish, or just string together emojis ("⭐⭐⭐⭐⭐ 🔥🔥🔥").
    *   *Mitigation*: Filter out reviews that contain no alphanumeric characters. For multi-language, rely on a multi-lingual embedding model (like `text-embedding-3-small`) that inherently groups semantic intent regardless of language.

---

## 2. Processing & Sanitization

*   **2.1 Aggressive PII False Positives**
    *   *Scenario*: The PII scrubber identifies a legitimate feature name (e.g., "Groww Pay") as a person's name and scrubs it, losing critical context.
    *   *Mitigation*: Use a whitelist of known product terms that the PII scrubber is forced to ignore.
*   **2.2 Context Window Overflow**
    *   *Scenario*: A single cluster contains 800 reviews. Passing all 800 into the LLM prompt exceeds the 128k/200k context window limit.
    *   *Mitigation*: Sample the reviews within the cluster. Select the top N reviews closest to the cluster centroid (using the embeddings) to represent the theme without overloading the prompt.

---

## 3. Reasoning & LLM Behavior

*   **3.1 Quote Hallucination & Validation Failure**
    *   *Scenario*: The LLM slightly rewrites a user quote to fix grammar, causing the strict substring validation check to fail.
    *   *Mitigation*: If the primary validation fails, trigger a fallback prompt explicitly commanding the LLM: "Extract exactly as written, do not change a single character." If it fails again, drop the quote for that theme.
*   **3.2 Megacluster "Junk Drawer"**
    *   *Scenario*: HDBSCAN fails to find distinct density peaks and groups 80% of reviews into a single massive cluster, resulting in a vague "General App Feedback" theme.
    *   *Mitigation*: Dynamically adjust `min_cluster_size` based on the total review count, or apply hierarchical sub-clustering if a single cluster exceeds a certain percentage of the dataset.

---

## 4. Delivery & MCP Server

*   **4.1 Google Docs Maximum Size Limits**
    *   *Scenario*: Over several years, the single running "Pulse" Google Doc hits Google's internal character or element limits and refuses to accept new appends.
    *   *Mitigation*: Detect `400 Bad Request (Doc too large)` errors in the MCP server. If caught, auto-create a new document (e.g., "Groww Pulse - Part 2") and link it from the old one.
*   **4.2 Partial Execution & Idempotency Conflicts**
    *   *Scenario*: The script appends the report to Google Docs successfully, but the container crashes *before* the MCP server can send the Gmail notification. On the next retry, the system tries to run again.
    *   *Mitigation*: Ensure the MCP Google Docs tool searches for the ISO week heading *first*. If it exists, it should return the existing heading link rather than appending a duplicate, allowing the script to proceed directly to sending the email.
*   **4.3 Manual Doc Interference**
    *   *Scenario*: A stakeholder accidentally deletes or renames the anchor heading (e.g., `Groww-Pulse-2023-W42`) in the Google Doc.
    *   *Mitigation*: Use hidden metadata/named ranges in the Google Doc if the API allows, or simply accept that manual deletion of the anchor will result in a duplicate append if a backfill is triggered.
*   **4.4 MCP Server Unavailability**
    *   *Scenario*: The agent finishes the heavy LLM processing, but the local MCP server fails to start or responds with a 500 error.
    *   *Mitigation*: Cache the final `PulseReport` JSON locally. Allow the CLI to be run in a `--delivery-only` mode that picks up the cached JSON and retries the MCP delivery without re-running the expensive LLM pipeline.
