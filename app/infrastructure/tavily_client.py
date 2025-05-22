from datetime import timezone, datetime

import asyncio

import os

from tavily import TavilyClient as TC

from crosscutting.logging.app_logger import AppLogger
from crosscutting.semantic_cache import SemanticCache


class TavilyClient:
    def __init__(self,
                 cache_path: str,
                 logger: AppLogger):
        self.logger = logger
        self.client = None
        self.cache = None
        self.cache_path = cache_path
        self.usage = 0
        self.cache_hits = 0

    async def search(self, query: str):
        """Executes searches on the web"""

        if not self.client:
            self.logger.debug("Initializing Tavily client ...")
            self.client = TC(os.environ.get("TAVILY_API_KEY"))
            self.cache = SemanticCache(self.cache_path, ttl_minutes=180)

        hit = self.cache.search(query)

        if hit:
            result, original_query, score = hit["result"], hit["match_query"], hit["score"]
            age = (datetime.now(timezone.utc) - datetime.fromisoformat(hit['timestamp'])).total_seconds() / 60
            self.logger.debug(f"Cache hit. Matched: '{query}' -> '{original_query}' (Score: {score:.3f}, Age: {age:.2f} minutes).")
            self.cache_hits += 1
            return result
        else:
            self.logger.debug(f"Calling client (Query: '{query}') ...")
            response = self.client.search(query=query)
            self.cache.store(query, response)
            self.usage += 1
            return response

    def save(self):
        self.logger.info(f"Tavily session usage: {self.usage} (+{self.cache_hits} cache hits).")
        if self.cache:
            self.cache.save()
            self.logger.info("Tavily cache flushed.")


if __name__ == "__main__":
    AppLogger.CONFIGS.is_structured = False
    client = TavilyClient(AppLogger())
    result = asyncio.run(client.search(query="Steve Jobs - Tech"))
    client.logger.debug(f"Result.", data=result)
    client.cache.save()