import asyncio

import http.client
import json
import os

from crosscutting.logging.app_logger import AppLogger


class SerperDevClient:

    async def search(self, query: str):
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


if __name__ == "__main__":
    AppLogger.CONFIGS.is_structured = False
    client = SerperDevClient()
    result = asyncio.run(client.search(query="Steve Jobs"))
    AppLogger.debug(f"Result.", data=result)