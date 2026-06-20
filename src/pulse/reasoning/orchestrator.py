import logging
from typing import List
from datetime import datetime

from pulse.models.domain import ScrubbedReview, PulseReport
from pulse.processing.embedder import ReviewEmbedder
from pulse.reasoning.clustering import ReviewClusterer
from pulse.reasoning.llm import GroqSummarizer

logger = logging.getLogger(__name__)

class PulseOrchestrator:
    def __init__(self, product_name: str, start_date: datetime, end_date: datetime):
        self.product_name = product_name
        self.start_date = start_date
        self.end_date = end_date
        
        self.embedder = ReviewEmbedder()
        self.clusterer = ReviewClusterer()
        self.llm = GroqSummarizer()
        
    def generate_report(self, reviews: List[ScrubbedReview]) -> PulseReport:
        logger.info(f"Starting Pulse Report generation for {self.product_name} with {len(reviews)} reviews.")
        
        # 1. Embed
        embeddings_dict = self.embedder.generate_embeddings(reviews)
        
        # 2. Cluster
        clusters_dict = self.clusterer.cluster_reviews(embeddings_dict)
        
        final_themes = []
        
        # 3. Summarize each cluster
        # Filter out the noise cluster (-1)
        valid_clusters = {k: v for k, v in clusters_dict.items() if k != -1}
        
        logger.info(f"Summarizing {len(valid_clusters)} valid clusters via LLM...")
        for label, cluster_reviews in valid_clusters.items():
            logger.info(f"Summarizing cluster {label} ({len(cluster_reviews)} reviews)...")
            cluster = self.llm.summarize_cluster(cluster_reviews)
            
            from pulse.models.domain import ThemeInsight
            insight = ThemeInsight(
                cluster_id=label,
                theme_name=cluster.theme_name,
                theme_summary=cluster.theme_summary,
                quotes=cluster.quotes,
                action_ideas=cluster.action_ideas
            )
            final_themes.append(insight)
            
        # 4. Calculate Stats
        total_reviews = len(reviews)
        stats = None
        rating_dist = None
        
        if total_reviews > 0:
            avg_rating = round(sum(r.rating for r in reviews) / total_reviews, 1)
            from collections import Counter
            counts = Counter(r.rating for r in reviews)
            
            from pulse.models.domain import ReportStats, RatingDistribution
            stats = ReportStats(total_reviews=total_reviews, average_rating=avg_rating)
            rating_dist = RatingDistribution(
                stars_1=round(counts.get(1, 0) / total_reviews * 100, 1),
                stars_2=round(counts.get(2, 0) / total_reviews * 100, 1),
                stars_3=round(counts.get(3, 0) / total_reviews * 100, 1),
                stars_4=round(counts.get(4, 0) / total_reviews * 100, 1),
                stars_5=round(counts.get(5, 0) / total_reviews * 100, 1),
            )

        logger.info("Report generated successfully.")
        return PulseReport(
            product_name=self.product_name,
            start_date=self.start_date,
            end_date=self.end_date,
            stats=stats,
            rating_distribution=rating_dist,
            themes=final_themes
        )
