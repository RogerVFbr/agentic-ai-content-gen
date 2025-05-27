import numpy as np
from rapidfuzz.distance import Levenshtein
from sentence_transformers import SentenceTransformer, util
from typing import List

from crosscutting.logging.app_logger import AppLogger
from infrastructure.google_trends_client import GoogleTrendsClient


class WebTrendsRepository:

    def __init__(self,
                 logger: AppLogger,
                 client: GoogleTrendsClient):

        self.logger = logger
        self.client = client
        self.model = None
        self.similarity_threshold: float = 0.60
        self.category_exclusion_filter = ["Sports", "Climate", "Politics"]

    async def get_trending_now(self, country: str, exclusion_list: List[str], limit: int = 10) -> List[dict]:
        if not self.model:
            self.logger.debug("Initializing WebTrendsRepository ...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')

        self.logger.debug("Calling client ...")
        result = await self.client.get_trending_now(country=country)
        exclusion_embeddings = self.model.encode([x.lower() for x in exclusion_list], convert_to_tensor=True)

        final_result = []

        for x in result:
            entry = {
                "trend_name": x.keyword,
                "trending_associated_keywords": x.trend_keywords[:5],
                "number_of_searches": x.volume,
                "volume_growth_pct": x.volume_growth_pct,
                "categories": [x for x in x.topic_names],
            }

            if any(category in self.category_exclusion_filter for category in entry["categories"]):
                continue

            if any(Levenshtein.distance(x.keyword.lower(), y.lower()) < 7 for y in exclusion_list):
                continue

            if len(exclusion_list) > 0:
                trend_embedding = self.model.encode(x.keyword.lower(), convert_to_tensor=True)
                similarities = util.cos_sim(trend_embedding, exclusion_embeddings)
                max_similarity = np.max(similarities.cpu().numpy())

                if max_similarity >= self.similarity_threshold:
                    continue

            final_result.append(entry)

            if len(final_result) >= limit:
                break

        return final_result