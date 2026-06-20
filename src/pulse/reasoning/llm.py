import os
import json
import random
import logging
from typing import List, Dict, Any
from groq import Groq
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from pulse.models.domain import ScrubbedReview, Cluster
from pulse.config import settings

logger = logging.getLogger(__name__)

class GroqSummarizer:
    def __init__(self):
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY is not set in the environment or .env file.")
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = "llama-3.3-70b-versatile"
        
    @retry(
        wait=wait_exponential(multiplier=1, min=4, max=60), 
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type(Exception) # Catch groq rate limit errors and retry
    )
    def _call_groq(self, prompt: str) -> str:
        logger.debug("Calling Groq API...")
        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert product manager analyzing user feedback. You always respond in valid JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=self.model,
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        # Type ignore because we know it exists based on the SDK
        return response.choices[0].message.content # type: ignore

    def _validate_quotes(self, generated_quotes: List[str], actual_reviews: List[ScrubbedReview]) -> List[str]:
        """Ensures generated quotes are exact substrings of the actual reviews to prevent hallucination."""
        valid_quotes = []
        actual_texts = [r.text.lower() for r in actual_reviews]
        for quote in generated_quotes:
            quote_lower = quote.lower()
            if any(quote_lower in text for text in actual_texts):
                valid_quotes.append(quote)
            else:
                logger.warning(f"Discarding hallucinated quote: '{quote}'")
        return valid_quotes

    def summarize_cluster(self, reviews: List[ScrubbedReview], max_sample_size: int = 15) -> Cluster:
        """
        Takes a cluster of reviews, samples them to stay under token limits, 
        and asks the LLM to generate a theme, quotes, and action ideas.
        """
        if len(reviews) > max_sample_size:
            sampled_reviews = random.sample(reviews, max_sample_size)
        else:
            sampled_reviews = reviews
            
        reviews_text = "\n".join([f"- {r.text}" for r in sampled_reviews])
        
        prompt = f"""
        Analyze the following cluster of user reviews for an app. These reviews have been algorithmically grouped because they share a common theme.
        
        Reviews:
        {reviews_text}
        
        Your task is to output a JSON object with exactly the following keys:
        - "theme_name": A short, punchy 2-5 word title for the overarching theme of these reviews.
        - "theme_summary": A 1-2 sentence summary explaining the core issue or sentiment of this theme.
        - "action_ideas": A list of 1-3 actionable ideas for the product team based on this feedback.
        - "quotes": A list of 1-3 direct, verbatim quotes from the reviews above that best represent the theme. DO NOT alter the quotes; they must be exact substrings of the provided text.
        
        JSON Output:
        """
        
        try:
            raw_response = self._call_groq(prompt)
            parsed = json.loads(raw_response)
            
            theme_name = parsed.get("theme_name", "Unknown Theme")
            theme_summary = parsed.get("theme_summary", "No summary provided.")
            action_ideas = parsed.get("action_ideas", [])
            raw_quotes = parsed.get("quotes", [])
            
            # Strict Quote Validation
            valid_quotes = self._validate_quotes(raw_quotes, sampled_reviews)
            
            return Cluster(
                theme_name=theme_name,
                theme_summary=theme_summary,
                quotes=valid_quotes,
                action_ideas=action_ideas,
                reviews=reviews, # keep the full list of reviews
            )
            
        except Exception as e:
            logger.error(f"Failed to summarize cluster: {e}")
            return Cluster(
                theme_name="Unsummarized Cluster", 
                theme_summary="Failed to summarize.",
                quotes=[],
                action_ideas=[],
                reviews=reviews
            )
