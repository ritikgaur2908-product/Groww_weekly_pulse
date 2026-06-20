import logging
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer

from pulse.models.domain import ScrubbedReview

logger = logging.getLogger(__name__)

class ReviewEmbedder:
    def __init__(self):
        logger.info("Loading lightweight TF-IDF embedder to bypass PyTorch DLL issues...")
        self.vectorizer = TfidfVectorizer(max_features=384, stop_words='english')
        
    def generate_embeddings(self, reviews: List[ScrubbedReview]) -> List[Dict[str, Any]]:
        """
        Generates vector embeddings for a list of ScrubbedReview objects using TF-IDF.
        """
        if not reviews:
            return []
            
        texts = [r.text for r in reviews]
        logger.info(f"Generating TF-IDF embeddings for {len(texts)} reviews...")
        
        embeddings = self.vectorizer.fit_transform(texts).toarray()
        
        results = []
        for review, emb in zip(reviews, embeddings):
            results.append({
                "review": review,
                "embedding": emb.tolist()
            })
            
        logger.info("Embeddings generation complete.")
        return results
