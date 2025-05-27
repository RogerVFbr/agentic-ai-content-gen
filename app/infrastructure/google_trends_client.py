#https://pypi.org/project/pytrends/
import asyncio
from trendspy import Trends

from crosscutting.logging.app_logger import AppLogger


class GoogleTrendsClient:

    def __init__(self):
        self.trendspy = None

    async def get_trending_now(self, country: str):
        if not self.trendspy:
            self.trendspy = Trends()

        result = self.trendspy.trending_now(geo=country)
        return sorted(result, key=lambda x: x.volume, reverse=True)

if __name__ == "__main__":
    AppLogger.CONFIGS.is_structured = False
    client = GoogleTrendsClient()
    a = asyncio.run(client.get_trending_now(country="US"))
    AppLogger.debug(f"Result.", data=a)
