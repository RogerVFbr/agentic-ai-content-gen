#https://pypi.org/project/pytrends/
import time

from typing import List

import json

from pytrends.request import TrendReq


class GoogleTrendsClient:

    def __init__(self):
        self.pytrend = TrendReq(hl='en-US', tz=360)

    def get_todays_top_searches_by_country(self, country: str):
        result_raw = self.pytrend.today_searches(pn=country).to_list()
        return [x.replace("&", "=").split("=")[1].replace("+", " ") for x in result_raw]

    def get_todays_realtime_trends_by_country(self, country: str, maxsize: int = 1000):
        result_raw = self.pytrend.trending_searches(pn=country).values.tolist()
        result = [item for sublist in result_raw for item in sublist]
        size = min(len(result), maxsize)
        return result[:size]

    def get_suggestions(self, keyword: str):
        result_raw = self.pytrend.suggestions(keyword=keyword)
        result = [{"title": x['title'], "type": x['type']} for x in result_raw]
        print(json.dumps(result, indent=4))
        return result

    def get_top_related_topics(self, keywords: List[str], max_size: int = 20):
        result = []
        for keyword in keywords:
            self.pytrend.build_payload(kw_list=[keyword])
            related_topics = self.pytrend.related_topics()
            keyword_top = [
                {
                    "title": x['topic_title'],
                    "type": x['topic_type'],
                    "value": x['value']
                } for x in list(related_topics.values())[0]['top'].to_dict('records')]
            result.extend(keyword_top)
            time.sleep(1)
        size = min(len(result), max_size)
        result = sorted(result, key=lambda d: d['value'], reverse=True)[:size]
        print(json.dumps(result, indent=4))
        return result

    def get_rising_related_topics(self, keywords: List[str], max_size: int = 20):
        result = []
        for keyword in keywords:
            self.pytrend.build_payload(kw_list=[keyword])
            related_topics = self.pytrend.related_topics()
            keyword_rising = [
                {
                    "title": x['topic_title'],
                    "type": x['topic_type'],
                    "value": x['value']
                } for x in list(related_topics.values())[0]['rising'].to_dict('records')]
            result.extend(keyword_rising)
            time.sleep(1)
        size = min(len(result), max_size)
        result = sorted(result, key=lambda d: d['value'], reverse=True)[:size]
        print(json.dumps(result, indent=4))
        return result

    def get_top_related_queries(self, keyword: str):
        self.pytrend.build_payload(kw_list=[keyword])
        related_queries = self.pytrend.related_queries()
        top = [x['query'] for x in list(related_queries.values())[0]['top'].to_dict('records')]
        print(json.dumps(top, indent=4))
        return top

    def get_rising_related_queries(self, keyword: str):
        self.pytrend.build_payload(kw_list=[keyword])
        related_queries = self.pytrend.related_queries()
        rising = [x['query'] for x in list(related_queries.values())[0]['rising'].to_dict('records')]
        print(json.dumps(rising, indent=4))
        return rising