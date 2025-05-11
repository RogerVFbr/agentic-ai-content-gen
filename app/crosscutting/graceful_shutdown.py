import signal

import asyncio


class GracefulShutdown:
    def __init__(self, loop):
        self.loop = loop
        self.cancel_event = asyncio.Event()

    def handle_signal(self, sig, _):
        print(f"[!] Received signal {sig.name}, initiating graceful shutdown.")
        self.cancel_event.set()

    def register(self):
        self.loop.add_signal_handler(signal.SIGINT, lambda: self.handle_signal(signal.SIGINT, None))
        self.loop.add_signal_handler(signal.SIGTERM, lambda: self.handle_signal(signal.SIGTERM, None))

    async def wait(self):
        await self.cancel_event.wait()