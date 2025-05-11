import asyncio
import signal
from abc import ABC, abstractmethod

class BackgroundService(ABC):
    def __init__(self):
        self._shutdown_event = asyncio.Event()
        self._loop = asyncio.get_running_loop()
        self._register_signal_handlers()

    async def run(self, input=None):
        """Entrypoint to start and manage the full lifecycle."""

        lifecycle_task = asyncio.create_task(self._lifecycle(input))
        shutdown_task = asyncio.create_task(self._shutdown_event.wait())

        done, _ = await asyncio.wait(
            [lifecycle_task, shutdown_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        if shutdown_task in done:
            lifecycle_task.cancel()
            try:
                await lifecycle_task
            except asyncio.CancelledError:
                pass
        else:
            shutdown_task.cancel()

    def _register_signal_handlers(self):
        for sig in (signal.SIGINT, signal.SIGTERM):
            self._loop.add_signal_handler(sig, self._shutdown_event.set)

    async def _lifecycle(self, input=None):
        try:
            await self.start(input)
        finally:
            await self.stop()

    @abstractmethod
    async def start(self, input=None):
        """To be implemented by subclass"""
        pass

    @abstractmethod
    async def stop(self):
        """To be implemented by subclass"""
        pass