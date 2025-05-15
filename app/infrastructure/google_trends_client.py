#https://pypi.org/project/pytrends/
from trendspy import Trends

from crosscutting.logging.app_logger import AppLogger


class GoogleTrendsClient:

    def __init__(self, logger: AppLogger):
        self.logger = logger
        self.trendspy = None

    # https://pypi.org/project/trendspy/

    async def get_trending_now(self, country: str):
        """Retrieve googles trending topics"""

        if not self.trendspy:
            self.logger.debug("Initializing GoogleTrendsClient ...")
            self.trendspy = Trends()

        self.logger.debug("Calling client ...")

        trends_with_news = self.trendspy.trending_now_by_rss(geo=country)

        result = []

        for x in trends_with_news:
            data = x.__dict__
            news = []
            for y in x.news:
                news.append(y.__dict__)
            data['news'] = news
            result.append(data)

        # print(json.dumps(result, indent=4, sort_keys=True, default=str))

        return result
