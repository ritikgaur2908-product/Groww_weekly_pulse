from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    groq_api_key: str = ""
    rolling_window_weeks: int = 8
    target_product_ids: List[str] = ["groww"]
    mcp_server_url: str = ""
    mcp_api_key: str = ""
    target_doc_id: str = ""
    target_email: str = ""
    max_reviews_budget: int = 500
    github_token: str = ""
    github_repo: str = "ritikgaur2908-product/Groww_weekly_pulse"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
