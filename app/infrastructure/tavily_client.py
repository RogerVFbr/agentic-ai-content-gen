import asyncio
import os
from tavily import TavilyClient as TC

from crosscutting.logging.app_logger import AppLogger


class TavilyClient:
    def __init__(self):
        self.client = None

    async def search(self, query: str):
        """Executes searches on the web"""

        if not self.client:
            self.client = TC(os.environ.get("TAVILY_API_KEY"))

        return self.client.search(query=query)


if __name__ == "__main__":
    AppLogger.CONFIGS.is_structured = False
    client = TavilyClient()
    result = asyncio.run(client.search(query="Steve Jobs - Tech"))
    AppLogger.debug(f"Result.", data=result)
