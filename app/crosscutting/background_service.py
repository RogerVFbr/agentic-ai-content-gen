import threading

import asyncio
import signal
from abc import ABC, abstractmethod


class CancellationToken:
    def __init__(self, event: threading.Event):
        self._event = event

    def is_cancellation_requested(self) -> bool:
        return self._event.is_set()

    def throw_if_cancellation_requested(self):
        if self._event.is_set():
            raise OperationCancelledException()

    def wait(self, timeout=None):
        return self._event.wait(timeout)

class CancellationTokenSource:
    def __init__(self):
        self._event = threading.Event()
        self.token = CancellationToken(self._event)

    def cancel(self):
        self._event.set()

    def is_cancellation_requested(self) -> bool:
        return self._event.is_set()

class OperationCancelledException(Exception):
    pass

class BackgroundService(ABC):
    def __init__(self):
        self._shutdown_event = asyncio.Event()
        self._loop = asyncio.get_running_loop()
        self._register_signal_handlers()
        self._cancellation_token_source = CancellationTokenSource()

    async def run(self, input=None):
        """Entrypoint to start and manage the full lifecycle."""

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

    def _register_signal_handlers(self):
        for sig in (signal.SIGINT, signal.SIGTERM):
            self._loop.add_signal_handler(sig, self._shutdown_event.set)

    async def _lifecycle(self, input=None):
        try:
            await self.start(self._cancellation_token_source.token, input)
        finally:
            await self.stop()

    @abstractmethod
    async def start(self, cancellation_token: CancellationToken, input=None):
        """To be implemented by subclass"""
        pass

    @abstractmethod
    async def stop(self):
        """To be implemented by subclass"""
        pass

    async def on_terminate(self):
        """To be optionally overridden by subclass"""
        pass