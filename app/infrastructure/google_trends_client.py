#https://pypi.org/project/pytrends/
import asyncio
import numpy as np
from rapidfuzz.distance import Levenshtein
from sentence_transformers import SentenceTransformer, util
from trendspy import Trends
from typing import List

from crosscutting.logging.app_logger import AppLogger


class GoogleTrendsClient:

    def __init__(self, logger: AppLogger):
        self.logger = logger
        self.trendspy = None
        self.model = None
        self.similarity_threshold: float = 0.60

    async def get_trending_now(self, country: str, exclusion_list: List[str]):
        """
        Retrieve the most recent trending topics from Google Trends for a specified country,
        excluding topics based on semantic similarity to an exclusion list.

        Args:
            country (str): The country code (e.g., "US") for which to retrieve trending topics.
            exclusion_list (List[str]): A list of keywords to exclude from the results..

        Returns:
            List[dict]: A list of dictionaries, each representing a trending topic.
        """
        if not self.trendspy:
            self.logger.debug("Initializing GoogleTrendsClient ...")
            self.trendspy = Trends()
            self.model = SentenceTransformer('all-MiniLM-L6-v2')

        self.logger.debug("Calling client ...", data=', '.join(exclusion_list))
        result = self.trendspy.trending_now(geo=country)
        result = sorted(result, key=lambda x: x.volume, reverse=True)

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

            if any(category in ["Sports", "Climate", "Politics"] for category in entry["categories"]):
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

        return final_result[:10]


if __name__ == "__main__":
    AppLogger.CONFIGS.is_structured = False
    client = GoogleTrendsClient(AppLogger())
    a = asyncio.run(client.get_trending_now(country="US", exclusion_list=[
        "uw platteville",
        "who won the voice 2025",
        "LEDGER",
        "amazing world of gumball",
        "ticket master",
        "the handmaid's tale",
        "jcpenney stores close"
    ]))
    client.logger.debug(f"Result.", data=a)
