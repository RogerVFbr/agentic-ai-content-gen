#https://pypi.org/project/pytrends/
from trendspy import Trends


class GoogleTrendsClient:

    def __init__(self):
        self._trendspy = None

    async def get_trending_now(self, country: str):
        if not self._trendspy:
            self._trendspy = Trends()

        result = self._trendspy.trending_now(geo=country)
        return sorted(result, key=lambda x: x.volume, reverse=True)
