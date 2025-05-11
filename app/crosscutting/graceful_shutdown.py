import asyncio


class GracefulShutdown:
    def __init__(self):
        self.cancel_event = None
        self.is_agent_running = None

    def reset(self):
        self.cancel_event = asyncio.Event()
        self.is_agent_running = True

    async def request(self):
        if self.cancel_event:
            self.cancel_event.set()
            while self.is_agent_running:
                await asyncio.sleep(1)

    async def wait(self):
        if self.cancel_event:
            await self.cancel_event.wait()

    def finish(self):
        self.is_agent_running = False