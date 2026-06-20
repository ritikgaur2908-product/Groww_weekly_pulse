import json
import logging
import os
from datetime import datetime, timedelta
from typing import List

from google_play_scraper import Sort, reviews

from pulse.models.domain import RawReview

logger = logging.getLogger(__name__)

def fetch_google_play_reviews(app_id: str, weeks: int) -> List[RawReview]:
    """
    Fetches reviews from the Google Play Store for a given app ID,
    filtered by a rolling window of weeks.
    
    Args:
        app_id: The package name of the app (e.g., 'com.nextbillion.groww')
        weeks: Number of weeks to look back from today
        
    Returns:
        A list of RawReview Pydantic objects.
    """
    cutoff_date = datetime.now() - timedelta(weeks=weeks)
    logger.info(f"Fetching reviews for {app_id} since {cutoff_date.date()}...")
    
    fetched_reviews: List[RawReview] = []
    continuation_token = None
    
    # Fetch in chunks to handle pagination gracefully
    while True:
        try:
            result, continuation_token = reviews(
                app_id,
                lang='en',
                country='in',  # Specifically targeting Indian market for Groww
                sort=Sort.NEWEST,
                count=100,
                continuation_token=continuation_token
            )
        except Exception as e:
            logger.error(f"Error fetching from Google Play: {e}")
            break
            
        if not result:
            break
            
        should_stop = False
        
        for review in result:
            review_date = review.get('at')
            if review_date and review_date < cutoff_date:
                should_stop = True
                break
                
            content = review.get('content')
            # Skip reviews without actual text content
            if not content or not str(content).strip():
                continue
                
            raw_review = RawReview(
                id=review.get('reviewId'),
                text=str(content).strip(),
                rating=review.get('score'),
                timestamp=review_date,
                source='Google Play'
            )
            fetched_reviews.append(raw_review)
            
        if should_stop or not continuation_token:
            break
            
    logger.info(f"Successfully fetched {len(fetched_reviews)} text-based reviews for {app_id}.")
    
    # Save to JSON
    try:
        # Resolve the absolute path to the project root's 'data/raw' folder
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        out_dir = os.path.join(project_root, "data", "raw")
        os.makedirs(out_dir, exist_ok=True)
        
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        file_path = os.path.join(out_dir, f"{app_id}_{timestamp_str}.json")
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([r.model_dump(mode='json') for r in fetched_reviews], f, indent=2)
        logger.info(f"Saved raw reviews to {file_path}")
    except Exception as e:
        logger.error(f"Failed to save raw reviews to JSON: {e}")

    return fetched_reviews
