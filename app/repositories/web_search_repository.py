from datetime import datetime, timezone
from pathlib import Path

from configurations.configs import Configs, WebSearchClient
from crosscutting.logging.app_logger import AppLogger
from crosscutting.semantic_cache import SemanticCache
from infrastructure.serper_dev_client import SerperDevClient
from infrastructure.tavily_client import TavilyClient


class WebSearchRepository:

    def __init__(self,
                 logger: AppLogger,
                 configs: Configs,
                 tavily_client: TavilyClient,
                 serper_dev_client: SerperDevClient):

        self.logger = logger
        self.configs = configs
        self.tavily_client = tavily_client
        self.serper_dev_client = serper_dev_client
        self.quota_usage = {}
        self.usage = 0
        self.cache_hits = 0
        self.cache = None


    async def search(self, node_name: str, query: str):
        """Executes searches on the web"""

        if not self.cache:
            self.cache = SemanticCache(
                str(Path.cwd() / self.configs.web_search.cache_path.lstrip("/")),
                ttl_minutes=self.configs.web_search.cache_ttl_minutes
            )

        if node_name not in self.quota_usage:
            self.quota_usage[node_name] = 0

        quota = self.configs.web_search.quota_per_node

        hit = self.cache.search(query)

        if hit:
            result, original_query, score = hit["result"], hit["match_query"], hit["score"]
            age = (datetime.now(timezone.utc) - datetime.fromisoformat(hit['timestamp'])).total_seconds() / 60
            self.logger.debug(f"Cache hit. Matched: '{query}' -> '{original_query}' (Score: {score:.3f}, Age: {age:.2f} minutes).")
            self.cache_hits += 1
            return result
        elif self.quota_usage[node_name] >= quota:
            self.logger.warn(f"Client quota exceeded for node '{node_name}' ({self.quota_usage[node_name]}/{quota}).")
            return {
                "error": "Client quota exceeded",
                "message": f"You have reached your application level search quota of {quota} searches."
            }
        elif self.configs.web_search.client == WebSearchClient.Tavily:
            self.logger.debug(f"Calling Tavily Client (Query: '{query}') ...")
            response = await self.tavily_client.search(query=query)
            self.cache.store(query, response)
            self.quota_usage[node_name] += 1
            self.usage += 1
            return response
        elif self.configs.web_search.client == WebSearchClient.SerperDev:
            self.logger.debug(f"Calling SerperDev Client (Query: '{query}') ...")
            response = await self.serper_dev_client.search(query=query)
            self.cache.store(query, response)
            self.quota_usage[node_name] += 1
            self.usage += 1
            return response
        else:
            raise Exception(f"Unknown client '{query}'.")

    def reset_quota(self, node_name: str):
        """Resets the usage quota."""
        self.quota_usage[node_name] = 0

    def save(self):
        self.logger.info(f"Web search session usage: {self.usage} (+{self.cache_hits} cache hits).")
        if self.cache:
            self.cache.save()
            self.logger.info("Web search cache flushed.")