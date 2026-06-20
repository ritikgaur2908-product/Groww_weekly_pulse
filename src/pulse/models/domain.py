from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class RawReview(BaseModel):
    id: str = Field(..., description="Unique identifier for the review")
    text: str = Field(..., description="The original review text")
    rating: int = Field(..., description="The star rating of the review (1-5)", ge=1, le=5)
    timestamp: datetime = Field(..., description="When the review was posted")
    source: str = Field(..., description="Platform the review came from, e.g. 'Google Play'")

class ScrubbedReview(BaseModel):
    original_id: str = Field(..., description="ID of the original raw review")
    text: str = Field(..., description="The review text with PII removed")
    rating: int
    timestamp: datetime

class ThemeInsight(BaseModel):
    cluster_id: int = Field(..., description="ID of the cluster")
    theme_name: str = Field(..., description="Short name of the theme")
    theme_summary: str = Field(..., description="1-2 sentence summary of the feedback in this theme")
    quotes: List[str] = Field(..., description="Verbatim quotes from users")
    action_ideas: List[str] = Field(..., description="Actionable ideas for the product team")

class Cluster(BaseModel):
    theme_name: str = Field(..., description="The name of the theme identified by the LLM")
    theme_summary: str = Field(..., description="Summary of the theme")
    quotes: List[str] = Field(default_factory=list, description="Validated quotes from this cluster")
    action_ideas: List[str] = Field(default_factory=list, description="Action ideas for this cluster")
    reviews: List[ScrubbedReview] = Field(..., description="List of scrubbed reviews belonging to this cluster")

class ReportStats(BaseModel):
    total_reviews: int = Field(..., description="Total number of reviews in the rolling window")
    average_rating: float = Field(..., description="Average rating of the reviews")

class RatingDistribution(BaseModel):
    stars_1: float = Field(..., description="Percentage of 1-star reviews")
    stars_2: float = Field(..., description="Percentage of 2-star reviews")
    stars_3: float = Field(..., description="Percentage of 3-star reviews")
    stars_4: float = Field(..., description="Percentage of 4-star reviews")
    stars_5: float = Field(..., description="Percentage of 5-star reviews")

class PulseReport(BaseModel):
    product_name: str = Field(..., description="Name of the product being reviewed")
    start_date: datetime = Field(..., description="Start of the rolling window")
    end_date: datetime = Field(..., description="End of the rolling window")
    stats: Optional[ReportStats] = Field(default=None, description="Overall review statistics")
    rating_distribution: Optional[RatingDistribution] = Field(default=None, description="Distribution of ratings as percentages")
    themes: List[ThemeInsight] = Field(default_factory=list, description="List of structured themes discovered")
