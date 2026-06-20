import logging
import numpy as np
from typing import List, Dict, Any
from sklearn.cluster import HDBSCAN
import umap

from pulse.models.domain import ScrubbedReview

logger = logging.getLogger(__name__)

class ReviewClusterer:
    def __init__(self, n_neighbors: int = 15, n_components: int = 5, min_cluster_size: int = 10):
        self.n_neighbors = n_neighbors
        self.n_components = n_components
        self.min_cluster_size = min_cluster_size

    def cluster_reviews(self, review_embeddings: List[Dict[str, Any]]) -> Dict[int, List[ScrubbedReview]]:
        """
        Takes a list of dictionaries with 'review' and 'embedding'.
        Reduces dimensionality using UMAP and clusters using HDBSCAN.
        Returns a dictionary mapping cluster_id -> List[ScrubbedReview].
        Cluster -1 represents noise/outliers and is usually excluded.
        """
        if not review_embeddings:
            logger.warning("No embeddings provided for clustering.")
            return {}

        embeddings_array = np.array([item["embedding"] for item in review_embeddings])
        
        num_reviews = embeddings_array.shape[0]
        
        # Dynamically adjust parameters for low review volumes
        actual_n_neighbors = min(self.n_neighbors, max(2, num_reviews - 1))
        actual_min_cluster_size = min(self.min_cluster_size, max(2, num_reviews // 2))

        logger.info(f"Reducing dimensions with UMAP ({num_reviews} samples, n_neighbors={actual_n_neighbors})...")
        reducer = umap.UMAP(
            n_neighbors=actual_n_neighbors, 
            n_components=self.n_components, 
            metric='cosine',
            random_state=42 # for reproducibility
        )
        reduced_embeddings = reducer.fit_transform(embeddings_array)

        logger.info(f"Clustering with HDBSCAN (min_cluster_size={actual_min_cluster_size})...")
        clusterer = HDBSCAN(
            min_cluster_size=actual_min_cluster_size,
            metric='euclidean',
            cluster_selection_method='eom'
        )
        labels = clusterer.fit_predict(reduced_embeddings)
        
        # Group reviews by cluster label
        clusters = {}
        for label, item in zip(labels, review_embeddings):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(item["review"])
            
        n_clusters = len(clusters) - (1 if -1 in clusters else 0)
        n_noise = len(clusters.get(-1, []))
        
        logger.info(f"Clustering complete: found {n_clusters} distinct clusters, with {n_noise} noise points.")
        return clusters
