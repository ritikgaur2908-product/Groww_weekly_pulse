import re
import logging
import emoji
from typing import List, Set
from pulse.models.domain import RawReview, ScrubbedReview

logger = logging.getLogger(__name__)

# Basic PII Regexes
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(r"\b(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\b")

# Spam/Gibberish Regexes
REPEATING_CHARS_REGEX = re.compile(r"(.)\1{4,}")

GENERIC_BLACKLIST = {
    "worst app ever",
    "please fix",
    "good app",
    "nice app",
    "very bad",
    "worst experience",
    "awsome app",
    "awesome app",
    "love this app",
    "bakwas app",
    "fake app",
    "worst app",
    "good",
    "nice",
    "bad",
    "excellent",
    "super",
    "superb"
}

def normalize_emoji_spam(text: str) -> str:
    """Collapses 3 or more repeating emojis into a single emoji."""
    if not text:
        return text
        
    result = []
    count = 0
    last_char = None
    
    for char in text:
        if emoji.is_emoji(char):
            if char == last_char:
                count += 1
                if count < 3: # Keep up to 2
                    result.append(char)
            else:
                last_char = char
                count = 1
                result.append(char)
        else:
            last_char = char
            count = 1
            result.append(char)
            
    return "".join(result)

def process_reviews(raw_reviews: List[RawReview]) -> List[ScrubbedReview]:
    """
    Applies PII scrubbing, emoji normalization, and robust filtering to a list of RawReviews.
    Returns a list of ScrubbedReview objects that pass all filters.
    """
    scrubbed_reviews = []
    seen_texts: Set[str] = set()
    
    dropped_counts = {
        "duplicates": 0,
        "gibberish": 0,
        "generic": 0,
        "low_word_count": 0,
    }

    for raw in raw_reviews:
        text = raw.text.strip()
        
        # 1. Exact Duplicates
        lower_text = text.lower()
        if lower_text in seen_texts:
            dropped_counts["duplicates"] += 1
            continue
        seen_texts.add(lower_text)
        
        # 2. Gibberish & Spam
        if REPEATING_CHARS_REGEX.search(text):
            dropped_counts["gibberish"] += 1
            continue
            
        # 3. Generic Sentiment
        clean_for_blacklist = re.sub(r"[^\w\s]", "", lower_text).strip()
        if clean_for_blacklist in GENERIC_BLACKLIST:
            dropped_counts["generic"] += 1
            continue
            
        # 4. PII Scrubbing
        text = EMAIL_REGEX.sub("[EMAIL]", text)
        text = PHONE_REGEX.sub("[PHONE]", text)
        
        # 5. Emoji Normalization
        text = normalize_emoji_spam(text)
        
        # 6. Low Word-Count & Emoji-Only
        text_without_emojis = emoji.replace_emoji(text, replace="")
        text_without_emojis = re.sub(r"\s+", " ", text_without_emojis).strip()
        
        words = text_without_emojis.split()
        if len(words) < 3:
            dropped_counts["low_word_count"] += 1
            continue
            
        # If it passes all filters, create ScrubbedReview
        scrubbed = ScrubbedReview(
            original_id=raw.id,
            text=text,
            rating=raw.rating,
            timestamp=raw.timestamp
        )
        scrubbed_reviews.append(scrubbed)
        
    logger.info(f"Sanitization complete. Started with {len(raw_reviews)}, retained {len(scrubbed_reviews)}.")
    logger.info(f"Dropped: {dropped_counts}")
    
    return scrubbed_reviews
