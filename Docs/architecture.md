# Weekly Product Review Pulse — Architecture Document

## 1. System Overview
The Weekly Product Review Pulse is an automated, scheduled system that aggregates, analyzes, and reports on public app store reviews. It relies on an agentic pipeline for data processing and a custom, locally provided Model Context Protocol (MCP) server for secure, abstracted delivery to Google Workspace (Google Docs and Gmail).

**Core Philosophy**: Separation of concerns. The core agent logic handles data ingestion, processing, and formatting. It delegates all delivery operations (writing to Docs, sending emails) to a dedicated MCP server. This keeps Google OAuth credentials out of the agent and provides a unified interface for system outputs.

---

## 2. System Components

### 2.1. Ingestion Module (Data Retrieval)
*   **Responsibility**: Fetch raw, public reviews from supported app stores (initially Google Play) over a configurable rolling window (e.g., 8–12 weeks).
*   **Mechanism**: Scraper-based extraction. 
*   **Output**: Standardized JSON/dataframes containing review text, rating, timestamp, and metadata.

### 2.2. Reasoning Engine (Processing & AI)
*   **Preprocessing**: PII scrubbing (removing names, emails, phone numbers from review text).
*   **Embeddings & Clustering**: 
    *   Converts review text into vector embeddings.
    *   Uses dimensionality reduction and density-based clustering (e.g., UMAP + HDBSCAN) to group semantically similar reviews into clusters.
*   **LLM Summarization**:
    *   Processes each cluster to identify a "Theme."
    *   Extracts real, verbatim quotes that represent the cluster.
    *   Proposes "Action Ideas" based on the clustered feedback.
    *   **Validation**: Ensures extracted quotes are exact substrings of the original review data to prevent LLM hallucinations.

### 2.3. Output Generator
*   **Responsibility**: Transforms the LLM's structured output into human-readable formats.
*   **Formats**:
    *   **Docs Payload**: A structured markdown or rich-text block containing the full pulse report.
    *   **Gmail Payload**: A concise HTML/text teaser summarizing top themes, with a deep link back to the Docs section.

### 2.4. Custom Google Workspace MCP Server (Delivery)
*   **Responsibility**: Exposes Google Docs and Gmail APIs as standardized MCP tools. The server is created separately and deployed to Railway (`https://web-production-e9833.up.railway.app/`).
*   **Authentication**: Manages Google Workspace OAuth credentials entirely within its own configuration.
*   **Tools Exposed**:
    *   `append_to_doc`: Appends a new section with a specific heading/anchor.
    *   `draft_email` / `send_email`: Creates or sends the teaser email to the stakeholder list.

### 2.5. Frontend Visualization App (Dashboard)
*   **Responsibility**: Provides a rich, interactive Web UI for stakeholders to visualize the generated reports.
*   **Key Features**:
    *   Displays historical reports via a sidebar navigation.
    *   Visualizes review volume, average ratings, and rating distributions.
    *   Presents an interactive, accordion-style view of discovered themes with quick access to LLM summaries, suggested actions, and raw verbatim quotes.

---

## 3. Data & Execution Flow

1.  **Trigger**: A GitHub Actions workflow (acting as a serverless cron job, e.g., Monday morning IST) invokes the main pipeline. CLI triggers are also supported for manual backfills of specific ISO weeks.
2.  **Ingestion**: The agent pulls recent reviews from the App Stores.
3.  **Sanitization**: Reviews pass through a PII scrubber.
4.  **Clustering**: Embeddings are generated and clustered to identify recurring themes.
5.  **LLM Processing**: The LLM names themes, extracts exact quotes, and suggests actions.
6.  **Rendering**: The agent formats the output into Docs and Email payloads.
7.  **Delivery via MCP**:
    *   The agent connects to the local **Google Workspace MCP Server**.
    *   It calls `append_to_doc`, passing the report payload. The MCP server returns the generated Doc Section ID / Anchor Link.
    *   The agent injects this Anchor Link into the Email payload.
    *   The agent calls `send_email` (or `draft_email` for staging) via the MCP server.

---

## 4. Key Architectural Decisions

### 4.1. Why MCP for Delivery?
Instead of hardcoding REST API calls to Google inside the agent, the MCP server abstracts these away. 
*   **Security**: The agent never sees the Google OAuth tokens.
*   **Modularity**: The delivery mechanism can be tested independently of the LLM/Processing logic. 
*   **Development Phasing**: Because the MCP server is decoupled, it will be developed separately in the later stages of the project, allowing the core ingestion and AI reasoning engines to be built and validated first.

### 4.2. Idempotency & State
Running the system twice for the same product and ISO week must not result in duplicate Doc sections or emails.
*   **Docs Idempotency**: The agent calculates a stable section anchor (e.g., `Groww-Pulse-2023-W42`). Before appending, the MCP server/tool checks if this anchor already exists. If yes, it aborts or updates the existing section.
*   **Email Idempotency**: Handled via run-scoped idempotency keys or by checking if a specific "Thread ID" or metadata tag exists for that ISO week before sending.

### 4.3. Hybrid Delivery: Web Dashboard + Docs
While the system originally relied solely on Google Docs as the UI, we have introduced a dedicated **Frontend Web Dashboard** to provide a rich, interactive experience (visualizing rating distributions, interactive theme accordions, and quick toggles for actions vs. raw quotes). 

Google Docs and Gmail are still used for frictionless push-notifications and archiving, but the Web Dashboard serves as the primary exploratory UI for deep dives into the data.

### 4.4. Serverless Execution & Scheduling via GitHub Actions
To guarantee 100% uptime and avoid issues with server sleep states on free-tier or local machines, the pipeline's execution schedule is entirely decoupled from any persistent hosting. We use GitHub Actions (`.github/workflows/pulse_schedule.yml`) to spin up a temporary runner, execute the CLI command, and spin down. This ensures reliability and provides built-in execution logs.

---

## 5. Security & Safety

*   **PII Scrubbing**: Strict regex and NLP-based scrubbing before data ever reaches the LLM.
*   **Data Integrity**: Reviews are treated strictly as data payloads. LLM prompts are hardened against prompt injection from malicious user reviews.
*   **Cost Controls**: Token limits and budget caps are enforced at the run-level to prevent runaway LLM costs on abnormally high-volume review weeks.
