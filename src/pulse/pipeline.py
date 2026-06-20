import json
import logging
import os
import glob
from datetime import datetime, timedelta

from pulse.models.domain import ScrubbedReview
from pulse.reasoning.orchestrator import PulseOrchestrator
from pulse.config import settings
from pulse.output.renderer import render_markdown_doc, render_email_html
from pulse.output.mcp_client import MCPClient
from pulse.output.github_client import upload_to_github
from pulse.auditing import log_audit_record

logger = logging.getLogger(__name__)

def get_latest_scrubbed_file(product: str) -> str:
    # Matches data/processed/*groww*scrubbed.json
    pattern = f"data/processed/*{product.lower()}*scrubbed.json"
    files = glob.glob(pattern)
    if not files:
        return None
    # return the latest modified file
    return max(files, key=os.path.getctime)

def run_pulse_pipeline(product: str, week: str = None, end_date_override: datetime = None):
    # If no week is provided, calculate it from end_date_override or today
    if not week:
        target_date = end_date_override or datetime.now()
        iso_year, iso_week, _ = target_date.isocalendar()
        week = f"{iso_year}-W{iso_week:02d}"

    logger.info(f"Starting Pulse Pipeline for {product.capitalize()} - Week {week}")
    
    # 1. Load the pre-processed scrubbed data
    data_path = get_latest_scrubbed_file(product)
    if not data_path:
        logger.error(f"Could not find scrubbed data for product {product}. Please run the processing script first.")
        return
        
    logger.info(f"Loading scrubbed data from {data_path}...")
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # Apply max_reviews_budget to avoid hitting Groq rate limits or excessive LLM costs
    if len(data) > settings.max_reviews_budget:
        logger.warning(f"Review count ({len(data)}) exceeds budget. Truncating to {settings.max_reviews_budget}.")
        data = data[:settings.max_reviews_budget]

    reviews = [ScrubbedReview(**r) for r in data]
    logger.info(f"Loaded {len(reviews)} reviews for processing.")
    
    if len(reviews) == 0:
        logger.warning(f"No reviews found for product {product} in this time period. Exiting pipeline.")
        return
    if end_date_override:
        end_date = end_date_override
    else:
        # Calculate dates from ISO week (e.g., 2026-W24)
        # 2026-W24-1 represents Monday of week 24
        try:
            end_date = datetime.strptime(f"{week}-1", "%G-W%V-%u") + timedelta(days=7)
        except ValueError:
            logger.error(f"Invalid week format: {week}. Please use ISO format like 2026-W24")
            return
        
    start_date = end_date - timedelta(weeks=8)

    # 2. Run the Reasoning Engine (Phase 4)
    orchestrator = PulseOrchestrator(
        product_name=product.capitalize(),
        start_date=start_date,
        end_date=end_date
    )
    
    # This will generate embeddings, cluster them, and call Groq to summarize
    report = orchestrator.generate_report(reviews)
    
    # 3. Save the report to disk
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    report_filename = f"data/reports/pulse_report_{product.lower()}_{timestamp}.json"
    
    logger.info(f"Saving final Pulse Report to {report_filename}...")
    with open(report_filename, "w", encoding="utf-8") as f:
        json_content = report.model_dump_json(indent=2)
        f.write(json_content)
        
    # NEW: Push to GitHub if configured (useful for ad-hoc UI reports on Railway)
    if settings.github_token and settings.github_repo:
        upload_to_github(
            token=settings.github_token,
            repo=settings.github_repo,
            file_path=report_filename,  # Format: data/reports/...json
            content=json_content
        )
        
    # 4. Delivery / Handoff via MCP Server
    doc_id = settings.target_doc_id
    email_draft_id = None
    
    if settings.mcp_server_url and settings.mcp_api_key:
        logger.info("Starting delivery via MCP server...")
        client = MCPClient(base_url=settings.mcp_server_url, api_key=settings.mcp_api_key)
        
        # 4a. Render and send to Docs
        markdown_content = render_markdown_doc(report)
        if doc_id:
            logger.info("Appending report to Google Doc...")
            success = client.append_to_doc(doc_id=doc_id, content=markdown_content)
            
            # 4b. Render and send Email (only if Doc succeeded)
            if success and settings.target_email:
                doc_link = f"https://docs.google.com/document/d/{doc_id}/edit"
                email_html = render_email_html(report, doc_link=doc_link)
                logger.info("Sending final email...")
                message_id = client.send_email(
                    to=settings.target_email,
                    subject=f"Pulse Report: {report.product_name} ({report.start_date.strftime('%b %d')} - {report.end_date.strftime('%b %d')})",
                    body=email_html
                )
                email_draft_id = message_id if message_id else None
        else:
            logger.warning("No TARGET_DOC_ID configured. Skipping Docs delivery.")
    else:
        logger.warning("MCP server URL or API Key missing. Skipping delivery phase.")

    # 5. Auditing (Phase 7)
    log_audit_record(
        product=product,
        week=week,
        doc_id=doc_id,
        email_draft_id=email_draft_id,
        status="SUCCESS"
    )

    logger.info("Pipeline completed successfully!")
