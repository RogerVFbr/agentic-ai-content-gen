import time
import asyncio


class GracefulShutdown:
    def __init__(self):
        self.loop = None
        self.cancel_event = None
        self.is_running = None

    def reset(self):
        self.loop = asyncio.get_running_loop()
        self.cancel_event = asyncio.Event()
        self.is_running = True

    async def request(self):
        self.cancel_event.set()
        while self.is_running:
            print("IMIN")
            await asyncio.sleep(1)


    async def wait(self):
        await self.cancel_event.wait()