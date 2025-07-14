import http.client
import json
import os


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