import json
import logging
import os
from datetime import datetime

from pulse.models.domain import ScrubbedReview
from pulse.reasoning.orchestrator import PulseOrchestrator
from pulse.config import settings
from pulse.output.renderer import render_markdown_doc, render_email_html
from pulse.output.mcp_client import MCPClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Pulse Pipeline...")
    
    # 1. Load the pre-processed scrubbed data
    data_path = "data/processed/com.nextbillion.groww_2026-06-10_230139_scrubbed.json"
    if not os.path.exists(data_path):
        logger.error(f"Could not find scrubbed data at {data_path}. Please run the processing script first.")
        return
        
    logger.info(f"Loading scrubbed data from {data_path}...")
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # Optional: limit to 200 reviews for testing speed and to avoid hitting Groq rate limits during local dev
    reviews = [ScrubbedReview(**r) for r in data[:200]] 
    logger.info(f"Loaded {len(reviews)} reviews for processing.")

    # 2. Run the Reasoning Engine (Phase 4)
    orchestrator = PulseOrchestrator(
        product_name="Groww",
        start_date=datetime(2026, 4, 15),
        end_date=datetime(2026, 6, 10)
    )
    
    # This will generate embeddings, cluster them, and call Groq to summarize
    report = orchestrator.generate_report(reviews)
    
    # 3. Save the report to disk
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    report_filename = f"data/reports/pulse_report_groww_{timestamp}.json"
    
    logger.info(f"Saving final Pulse Report to {report_filename}...")
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2))
        
    # 4. Delivery / Handoff via MCP Server
    if settings.mcp_server_url and settings.mcp_api_key:
        logger.info("Starting delivery via MCP server...")
        client = MCPClient(base_url=settings.mcp_server_url, api_key=settings.mcp_api_key)
        
        # 4a. Render and send to Docs
        markdown_content = render_markdown_doc(report)
        doc_id = settings.target_doc_id
        if doc_id:
            logger.info("Appending report to Google Doc...")
            success = client.append_to_doc(doc_id=doc_id, content=markdown_content)
            
            # 4b. Render and send Email (only if Doc succeeded)
            if success and settings.target_email:
                doc_link = f"https://docs.google.com/document/d/{doc_id}/edit"
                email_html = render_email_html(report, doc_link=doc_link)
                logger.info("Creating Gmail draft...")
                client.create_email_draft(
                    to=settings.target_email,
                    subject=f"Pulse Report: {report.product_name} ({report.start_date.strftime('%b %d')} - {report.end_date.strftime('%b %d')})",
                    body=email_html
                )
        else:
            logger.warning("No TARGET_DOC_ID configured. Skipping Docs delivery.")
    else:
        logger.warning("MCP server URL or API Key missing. Skipping delivery phase.")

    logger.info("Pipeline completed successfully!")

if __name__ == "__main__":
    main()
