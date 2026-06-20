import requests
import base64
import logging
import os

logger = logging.getLogger(__name__)

def upload_to_github(token: str, repo: str, file_path: str, content: str) -> bool:
    """
    Uploads a file to a GitHub repository using the GitHub REST API.
    Uses PUT /repos/{owner}/{repo}/contents/{path}.
    
    Args:
        token: GitHub Personal Access Token
        repo: Repository format "owner/repo" (e.g. "ritikgaur2908-product/Groww_weekly_pulse")
        file_path: Target path in the repo (e.g. "data/reports/pulse_report_groww_xxx.json")
        content: The text content to upload
        
    Returns:
        bool: True if successful, False otherwise.
    """
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    
    # Base64 encode the content as required by the GitHub API
    content_bytes = content.encode("utf-8")
    b64_content = base64.b64encode(content_bytes).decode("utf-8")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    # Extract filename for the commit message
    filename = os.path.basename(file_path)
    
    payload = {
        "message": f"Auto-generate pulse report: {filename}",
        "content": b64_content,
        "branch": "main"  # Always target the main branch
    }
    
    try:
        logger.info(f"Uploading {file_path} to GitHub repo {repo}...")
        response = requests.put(url, json=payload, headers=headers)
        
        # 201 Created or 200 OK (if updating an existing file)
        if response.status_code in [200, 201]:
            logger.info(f"Successfully uploaded {file_path} to GitHub!")
            return True
        else:
            logger.error(f"Failed to upload to GitHub: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Exception during GitHub upload: {e}")
        return False
