from datetime import datetime, timezone

import asyncio

import http.client
import json
import os

from crosscutting.logging.app_logger import AppLogger
from crosscutting.semantic_cache import SemanticCache


class SerperDevClient:

    CACHE_PATH = "serper_dev_cache.json"

    CACHE = None

    def __init__(self,
                 cache_path: str,
                 quota: int,
                 logger: AppLogger):

        self.logger = logger
        self.cache = None
        self.cache_path = cache_path
        self.quota = quota
        self.quota_usage = 0
        self.usage = 0
        self.cache_hits = 0

    async def search(self, query: str):
        """
        Searches the web using the Serper.dev API.

        This method sends a POST request to the Serper.dev API with the provided query string
        and retrieves search results in JSON format. It uses the `SERPERDEV_API_KEY` environment
        variable for authentication.

        Args:
            query (str): The search query string to be sent to the Serper.dev API.

        Returns:
            dict: A dictionary containing the search results with the following structure:

        {
            "searchParameters": {
                "q": "Steve Jobs",
                "type": "search",
                "engine": "google"
            },
            "knowledgeGraph": {
                "title": "Steve Jobs",
                "type": "Former CEO of Apple",
                "imageUrl": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSeAKJ0CPa-i0BDi3js8rSXhTalzisu2-ZUmX5JiA&s=0",
                "description": "Steven Paul Jobs was an American businessman, inventor, and investor best known for co-founding the technology company Apple Inc. Jobs was also the founder of NeXT and chairman and majority shareholder of Pixar.",
                "descriptionSource": "Wikipedia",
                "descriptionLink": "https://en.wikipedia.org/wiki/Steve_Jobs",
                "attributes": {
                    "Born": "February 24, 1955, San Francisco, CA",
                    "Died": "October 5, 2011 (age 56 years), Palo Alto, CA",
                    "Spouse": "Laurene Powell Jobs (m. 1991–2011)",
                    "Children": "Eve Jobs, Reed Jobs, Erin Siena Jobs, and more",
                    "Education": "Homestead High School (1968–1972), Reed College (1972–1972), Monta Loma Elementary, and more",
                    "Parents": "Abdulfattah John Jandali, Joanne Schieble Simpson, Paul Jobs, and more",
                    "Height": "6′ 2″"
                }
            },
            "organic": [
                {
                    "title": "Steve Jobs - Wikipedia",
                    "link": "https://en.wikipedia.org/wiki/Steve_Jobs",
                    "snippet": "Steven Paul Jobs (February 24, 1955 – October 5, 2011) was an American businessman, inventor, and investor best known for co-founding the technology company ...",
                    "sitelinks": [
                        {
                            "title": "Steve Wozniak",
                            "link": "https://en.wikipedia.org/wiki/Steve_Wozniak"
                        },
                        {
                            "title": "List of depictions of Steve Jobs",
                            "link": "https://en.wikipedia.org/wiki/List_of_depictions_of_Steve_Jobs"
                        }
                    ],
                    "position": 1
                },
                {
                    "title": "Remembering Steve Jobs - Apple",
                    "link": "https://www.apple.com/stevejobs/",
                    "snippet": "He was a visionary that had the amazing ability to breath life into his ideas. He believed so passionately in his work that his creativity became both seductive ...",
                    "position": 2
                }
            ],
            "images": [
                {
                    "title": "encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcSkKG...",
                    "imageUrl": "https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcSkKGZuRUelGLq0FpwuFi9fp7fEPejRm5qgBKO2AQXBQ5VWl1Wf",
                    "link": "http://google.com/search?tbm=isch&q=Steve+Jobs"
                },
                {
                    "title": "Steve Jobs - Wikipedia",
                    "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/d/dc/Steve_Jobs_Headshot_2010-CROP_%28cropped_2%29.jpg",
                    "link": "https://en.wikipedia.org/wiki/Steve_Jobs"
                }
            ],
            "relatedSearches": [
                {
                    "query": "Mark Zuckerberg"
                },
                {
                    "query": "Steve Jobs book"
                }
            ],
            "credits": 1
        }
        """

        if not self.cache:
            self.logger.debug("Initializing SerperDevClient client ...")
            self.cache = SemanticCache(self.cache_path, ttl_minutes=180)

        hit = self.cache.search(query)

        if hit:
            result, original_query, score = hit["result"], hit["match_query"], hit["score"]
            age = (datetime.now(timezone.utc) - datetime.fromisoformat(hit['timestamp'])).total_seconds() / 60
            self.logger.debug(f"Cache hit. Matched: '{query}' -> '{original_query}' (Score: {score:.3f}, Age: {age:.2f} minutes).")
            self.cache_hits += 1
            return result
        elif self.quota_usage >= self.quota:
            self.logger.warn(f"Client quota exceeded ({self.quota_usage}/{self.quota}).")
            return {
                "error": "Client quota exceeded",
                "message": f"You have reached your application level search quota of {self.quota} searches."
            }
        else:
            self.logger.debug(f"Calling client (Query: '{query}') ...")
            conn = http.client.HTTPSConnection("google.serper.dev")
            payload = json.dumps({
                "q": query
            })
            headers = {
                'X-API-KEY': os.environ.get("SERPERDEV_API_KEY"),
                'Content-Type': 'application/json'
            }
            conn.request("POST", "/search", payload, headers)
            res = conn.getresponse()
            data = res.read()
            data = data.decode("utf-8")
            result = json.loads(data)
            self.cache.store(query, result)
            self.usage += 1
            return result

    def reset_quota(self):
        """Resets the usage quota."""
        self.quota_usage = 0

    def save(self):
        self.logger.info(f"SerperDevClient session usage: {self.usage} (+{self.cache_hits} cache hits).")
        if self.cache:
            self.cache.save()
            self.logger.info("SerperDevClient cache flushed.")


if __name__ == "__main__":
    AppLogger.CONFIGS.is_structured = False
    client = SerperDevClient(AppLogger())
    result = asyncio.run(client.search(query="Steve Jobs"))
    client.logger.debug(f"Result.", data=result)