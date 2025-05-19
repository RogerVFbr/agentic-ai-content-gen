from datetime import timezone, datetime

import asyncio

import os

from tavily import TavilyClient as TC

from crosscutting.logging.app_logger import AppLogger
from crosscutting.semantic_cache import SemanticCache


class TavilyClient:
    def __init__(self,
                 logger: AppLogger):
        self.logger = logger
        self.client = None
        self.cache = None
        self.cache_path = os.path.join(os.getcwd(), "tavily_cache.pkl")

    async def search(self, query: str):

        if not self.client:
            self.logger.debug("Initializing Tavily client ...")
            self.client = TC(os.environ.get("TAVILY_API_KEY"))
            self.logger.debug("Initializing cache ...")
            self.cache = SemanticCache(self.cache_path, ttl_minutes=180)

        hit = self.cache.search(query)

        if hit:
            result = hit["result"]
            original_query = hit["match_query"]
            score = hit["score"]
            self.logger.debug(f"Cache hit. Matched: '{query}' -> '{original_query}' (Score: {score:.3f}, Age: {(datetime.now(timezone.utc) - datetime.fromisoformat(hit['timestamp'])).total_seconds() / 60:.2f} minutes).")
            return result
        else:
            self.logger.debug(f"Calling client (Query: '{query}') ...")
            response = self.client.search(query=query)
            self.cache.store(query, response)
            return response


if __name__ == "__main__":
    AppLogger.CONFIGS.is_structured = False
    client = TavilyClient(AppLogger())
    result = asyncio.run(client.search(query="Steve Jobs - Tech"))
    client.logger.debug(f"Result.", data=result)
    client.cache.save()