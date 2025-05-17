#https://pypi.org/project/pytrends/
from rapidfuzz.distance import Levenshtein
from typing import List

import asyncio

import json

from trendspy import Trends

from crosscutting.logging.app_logger import AppLogger


class GoogleTrendsClient:

    def __init__(self, logger: AppLogger):
        self.logger = logger
        self.trendspy = None

    # https://pypi.org/project/trendspy/

    async def get_trending_now(self, country: str, exclusion_list: List[str]):
        """
        Retrieve the most recent trending topics from Google Trends for a specified country,
        excluding topics based on an exclusion list.

        Args:
            country (str): The country code (e.g., "US") for which to retrieve trending topics.
            exclusion_list (List[str]): A list of keywords to exclude from the results.

        Returns:
            List[dict]: A list of dictionaries, each representing a trending topic. Each dictionary
            contains the following keys:
                - "trend_name" (str): The name of the trending topic.
                - "trending_associated_keywords" (List[str]): A list of associated keywords for the trend.
                - "number_of_searches" (int): The search volume for the trend.
                - "volume_growth_pct" (float): The percentage growth in search volume.
                - "categories" (List[str]): A list of categories associated with the trend.

        Raises:
            Exception: If the `trendspy` client fails to initialize or retrieve data.
        """

        if not self.trendspy:
            self.logger.debug("Initializing GoogleTrendsClient ...")
            self.trendspy = Trends()

        self.logger.debug("Calling client ...")

        result = self.trendspy.trending_now(geo=country)
        result = sorted(result, key=lambda x: x.volume, reverse=True)

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

            final_result.append(entry)

        return final_result[:6]


if __name__ == "__main__":
    AppLogger.CONFIGS.is_structured = False
    client = GoogleTrendsClient(AppLogger())
    a = asyncio.run(client.get_trending_now(country="US", exclusion_list=["tornado watch", "seviille"]))
    client.logger.debug(f"Result.", data=a)
