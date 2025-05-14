import http.client
import json
import os

from crosscutting.logging.app_logger import AppLogger


class SerperDevClient:

    def __init__(self,
                 logger: AppLogger):

        self.logger = logger


    def search(self, query):
        """Searches the web using the Serper.dev API."""

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
        return json.loads(data)