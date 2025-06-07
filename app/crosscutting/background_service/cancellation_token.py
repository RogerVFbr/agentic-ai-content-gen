import threading


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