import asyncio
import signal
from abc import ABC, abstractmethod

from crosscutting.cancellation_token import CancellationTokenSource, CancellationToken


class OneShotBackgroundService(ABC):
    def __init__(self):
        self._shutdown_event = None
        self._loop = None
        self._cancellation_token_source = None

    async def run(self, input=None):
        """Entrypoint to start and manage the full lifecycle."""

        self._shutdown_event = asyncio.Event()
        self._loop = asyncio.get_running_loop()
        self._cancellation_token_source = CancellationTokenSource()
        self._register_signal_handlers()

        lifecycle_task = asyncio.create_task(self._lifecycle(input))
        shutdown_task = asyncio.create_task(self._shutdown_event.wait())

        done, _ = await asyncio.wait(
            [lifecycle_task, shutdown_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        if shutdown_task in done:
            self._cancellation_token_source.cancel()
            await self.on_terminate()
            lifecycle_task.cancel()
            try:
                await lifecycle_task
            except asyncio.CancelledError:
                pass
        else:
            shutdown_task.cancel()
            if lifecycle_task.exception():
                raise lifecycle_task.exception()

    def _register_signal_handlers(self):
        for sig in (signal.SIGINT, signal.SIGTERM):
            self._loop.add_signal_handler(sig, self._set_shutdown_event)

    def _set_shutdown_event(self):
        """Set the shutdown event to signal termination."""
        if self._shutdown_event:
            self._shutdown_event.set()

    async def _lifecycle(self, input=None):
        try:
            await self.on_initialize()
            await self.start(self._cancellation_token_source.token, input)
        finally:
            await self.stop(self._cancellation_token_source.token)

    @abstractmethod
    async def start(self, cancellation_token: CancellationToken, input=None):
        """To be implemented by subclass"""
        pass

    @abstractmethod
    async def stop(self, cancellation_token: CancellationToken, input=None):
        """To be implemented by subclass"""
        pass

    async def on_initialize(self):
        """To be optionally overridden by subclass"""
        pass

    async def on_terminate(self):
        """To be optionally overridden by subclass"""
        pass