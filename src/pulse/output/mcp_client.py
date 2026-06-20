import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class MCPClient:
    """
    Client for communicating with the custom Google Workspace MCP Server.
    """
    def __init__(self, base_url: str, api_key: str):
        # Ensure base URL doesn't have a trailing slash
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key
        }

    def append_to_doc(self, doc_id: str, content: str) -> bool:
        """
        Sends the markdown content to the MCP server to append to the Google Doc.
        Returns True if successful, False otherwise.
        """
        url = f"{self.base_url}/append_to_doc"
        payload = {
            "doc_id": doc_id,
            "content": content
        }
        
        try:
            logger.info(f"Sending append_to_doc request to {url}")
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            logger.info("Successfully appended to Google Doc.")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to append to Google Doc: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return False

    def create_email_draft(self, to: str, subject: str, body: str) -> Optional[str]:
        """
        Sends the HTML content to the MCP server to create a Gmail draft.
        Returns the draft ID if successful, None otherwise.
        """
        url = f"{self.base_url}/create_email_draft"
        payload = {
            "to": to,
            "subject": subject,
            "body": body
        }
        
        try:
            logger.info(f"Sending create_email_draft request to {url}")
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            draft_id = data.get("draft_id")
            logger.info(f"Successfully created email draft. Draft ID: {draft_id}")
            return draft_id
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create email draft: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return None

    def send_email(self, to: str, subject: str, body: str) -> Optional[str]:
        """
        Sends the HTML content to the MCP server to directly send an email.
        Returns the message ID if successful, None otherwise.
        """
        url = f"{self.base_url}/send_email"
        payload = {
            "to": to,
            "subject": subject,
            "body": body
        }
        
        try:
            logger.info(f"Sending send_email request to {url}")
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            message_id = data.get("message_id")
            logger.info(f"Successfully sent email. Message ID: {message_id}")
            return message_id
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send email: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return None
