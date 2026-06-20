import json
import os
from datetime import datetime
from typing import Optional

AUDIT_LOG_FILE = "data/audit_log.jsonl"

def log_audit_record(product: str, week: str, doc_id: Optional[str], email_draft_id: Optional[str], status: str):
    """
    Appends an audit record to the local JSON Lines file.
    """
    os.makedirs(os.path.dirname(AUDIT_LOG_FILE), exist_ok=True)
    
    record = {
        "timestamp": datetime.now().isoformat(),
        "product": product,
        "week": week,
        "status": status,
        "doc_id": doc_id,
        "email_draft_id": email_draft_id
    }
    
    with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
