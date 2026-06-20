# Weekly Product Review Pulse — Implementation Plan

This document outlines a detailed, phase-wise implementation plan for the Weekly Product Review Pulse system. It is designed to be executed sequentially, building the core data processing and AI reasoning engines first, and then developing the custom MCP server for delivery in the later stages.

---

## Phase 1: Project Initialization & Core Scaffolding
**Goal**: Establish the project environment, architecture boundaries, and foundational data structures.
*   **1.1 Repository Setup**: Initialize the project (e.g., Python using `Poetry` or `uv`), configure linting (`ruff`/`black`), and set up the directory structure.
*   **1.2 Define Data Models**: Create strict schema definitions (e.g., using `Pydantic`) for:
    *   `RawReview` (id, text, rating, timestamp, source).
    *   `ScrubbedReview` (text without PII).
    *   `Cluster` (theme name, list of related reviews).
    *   `PulseReport` (final structured data containing themes, quotes, and action items).
*   **1.3 Configuration Management**: Set up environment variable handling for API keys (LLM), thresholds (rolling window weeks), and target product IDs.

---

## Phase 2: Data Ingestion (App Stores)
**Goal**: Safely retrieve raw reviews from target platforms based on configurable time windows.
*   **2.1 Google Play Scraper**: Implement or integrate a scraper (e.g., `google-play-scraper` in Python) to fetch reviews for a given package ID (e.g., Groww).
*   **2.2 Time-Window Filtering**: Add logic to calculate the exact start and end dates for the "Last 8–12 weeks" rolling window, fetching only relevant reviews.
*   **2.3 Data Normalization**: Map the scraper output to the `RawReview` Pydantic models defined in Phase 1.

---

## Phase 3: Data Processing & Sanitization
**Goal**: Clean the data and prepare it for AI reasoning.
*   **3.1 PII & Emoji Scrubbing**: 
    *   Implement regex-based and lightweight NLP scrubbing to detect and mask emails, phone numbers, and names in review text.
    *   Normalize emoji spam (e.g., collapsing `🚀🚀🚀` to `🚀`) while preserving meaningful emojis for sentiment analysis.
*   **3.2 Review Filtering**: Filter out non-actionable reviews to save LLM tokens and improve clustering quality. Filtering conditions include:
    *   **Low Word-Count**: Dropping reviews with fewer than 3-4 words (after stripping emojis).
    *   **Emoji-Only**: Dropping reviews that consist entirely of emojis without text.
    *   **Gibberish & Spam**: Removing reviews with excessive repeated characters or punctuation.
    *   **Exact Duplicates**: Deduplicating identical reviews to prevent cluster skewing.
    *   **Generic Sentiment**: Dropping common, non-actionable phrases like "worst app ever" or "please fix".
*   **3.3 Embeddings Generation**: Pass the scrubbed text through the local `BAAI/bge-small-en-v1.5` SentenceTransformer model to get vector representations. This free, open-source model runs entirely locally.

---

## Phase 4: Reasoning Engine (Clustering & LLM)
**Goal**: Group similar feedback and use an LLM to generate insights.
*   **4.1 Dimensionality Reduction**: Implement `UMAP` to reduce embedding dimensions for efficient clustering.
*   **4.2 Density-Based Clustering**: Implement `HDBSCAN` to group the reduced embeddings into distinct review clusters.
*   **4.3 LLM Summarization Pipeline (Groq)**:
    *   **Model Strategy**: Use Groq's `llama-3.3-70b-versatile` model for inference.
    *   **Cluster Sampling**: Due to strict token limits, sample only the top 10-15 most representative reviews (e.g., closest to the cluster centroid) from each cluster to keep prompt sizes small.
    *   **Rate Limit Handling**: Implement an explicit rate-limiter and exponential backoff (e.g., via `tenacity` or `asyncio.sleep`) to strictly respect Groq's limits: 30 Requests Per Minute and 12,000 Tokens Per Minute. The pipeline must dynamically pause execution if it approaches these limits across multiple clusters.
    *   **Prompting**: Design prompts to extract a "Theme Name", "Action Ideas", and representative "Quotes" from the sampled reviews.
    *   **Strict Quote Validation**: Implement a validation step that forcefully checks if the LLM-generated quotes are exact substrings of the original `ScrubbedReview` text. Reject or retry on hallucinated quotes.
*   **4.4 Report Assembly**: Aggregate the themes, validated quotes, and action items into the final `PulseReport` model.

---

## Phase 5: Custom Google Workspace MCP Server Development
**Goal**: Build and independently test the local MCP server responsible for all Google integrations, ensuring it is ready to be plugged into the main agent's output flow. *(Deployed to Railway at: `https://web-production-e9833.up.railway.app/`)*
*   **5.1 MCP Server Scaffolding**: Initialize a standard MCP server using the official Python/Node SDK.
*   **5.2 Authentication Flow**: Configure Google Workspace credentials (e.g., Service Account JSON) securely within the server’s local environment.
*   **5.3 Implement Google Docs Tool (`append_to_doc`)**:
    *   Build the logic to append markdown/rich text to a specific Google Doc ID.
    *   **Idempotency Logic**: Implement a check to scan for existing section anchors (e.g., `Groww-Pulse-2023-W42`) before appending to prevent duplicates.
*   **5.4 Implement Gmail Tools (`draft_email` / `send_email`)**:
    *   Build the ability to create HTML/text emails.
    *   **Idempotency Logic**: Implement Thread ID checking or custom email headers to ensure a weekly report isn't sent twice.
*   **5.5 Independent Testing**: Use an MCP inspector or dummy client to verify the server correctly modifies a test Doc and drafts a test email.

---

## Phase 6: Output Generation & MCP Client Integration
**Goal**: Format the insights and send them to the MCP server for delivery.
*   **6.1 Rendering Engine**:
    *   Create a template for the Google Doc payload (markdown/structured).
    *   Create a template for the Gmail teaser (HTML) containing a deep link to the Doc.
*   **6.2 MCP Client Implementation**: Integrate an MCP Client within the agent code to connect to the custom server built in Phase 5.
*   **6.3 End-to-End Handoff**: 
    *   Pass the rendered Doc payload to `append_to_doc`.
    *   Retrieve the deep link/anchor from the response.
    *   Pass the rendered Email payload (with deep link) to `draft_email` (defaulting to draft during testing).

---

## Phase 7: Orchestration, CLI, and Scheduling
**Goal**: Wrap the pipeline in a reliable, scheduled executable.
*   **7.1 CLI Interface**: Build a Command Line Interface (e.g., using `Typer` or `Click`) allowing operators to run `pulse run --product groww --week 2023-W42`.
*   **7.2 State & Auditing**: Implement lightweight local logging or a SQLite database to record run identifiers (Week, Doc Heading ID, Email Message ID) to fulfill the auditability requirement.
*   **7.3 Scheduling**: Create a `.github/workflows/pulse_schedule.yml` file to handle serverless execution via GitHub Actions. This workflow will install dependencies, inject secrets, and trigger the CLI automatically (e.g., Monday morning IST).

---

## Phase 8: Hardening & Production Release
**Goal**: Ensure the system is robust, safe, and ready for stakeholders.
*   **8.1 Edge-Case Handling**: Add handling for weeks with extremely low review volume (skip or adjust clustering parameters).
*   **8.2 Cost Constraints**: Implement circuit breakers to stop processing if the review volume exceeds token budget limits.
*   **8.3 Staging Run**: Perform an end-to-end dry run generating a real Google Doc and drafting an email for stakeholder review.
*   **8.4 Go-Live**: Switch the MCP server from `draft_email` to `send_email` and activate the cron schedule.

---

## Phase 9: Web UI Dashboard (Interactive Visualization)
**Goal**: Build a dedicated, interactive Web Dashboard for stakeholders to explore the JSON reports dynamically.
*   **9.1 Frontend Framework Setup**: Initialize a modern React-based application (e.g., Next.js or Vite).
*   **9.2 Layout Implementation (LHS/RHS)**:
    *   Build the LHS Sidebar for report history/navigation.
    *   Build the RHS Main Content area featuring the dynamic Hero Section, Stats row, and Rating Distribution bar graph.
*   **9.3 Interactive Theme Viewer**:
    *   Implement an accordion or stacked list for discovered themes.
    *   Build the dynamic detail view below the selected theme, including the summary and default "Actions" vs "Reviews" tabs.
*   **9.4 Data Binding**: Connect the UI to the local `data/reports/*.json` files or build an API to serve the generated Pulse Reports.
