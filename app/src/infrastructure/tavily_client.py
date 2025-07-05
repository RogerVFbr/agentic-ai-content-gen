import os
from tavily import TavilyClient as TC



class TavilyClient:
    def __init__(self):
        self.client = None

    async def search(self, query: str):
        """Executes searches on the web"""

        if not self.client:
            self.client = TC(os.environ.get("TAVILY_API_KEY"))

        return self.client.search(query=query)
