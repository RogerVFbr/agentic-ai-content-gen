import pytest
import threading
from crosscutting.cancellation_token import CancellationToken, CancellationTokenSource, OperationCancelledException


class TestCancellationToken:

    @pytest.fixture
    def token_source(self) -> CancellationTokenSource:
        return CancellationTokenSource()

    @pytest.fixture
    def token(self, token_source: CancellationTokenSource) -> CancellationToken:
        return token_source.token

    def test_is_cancellation_requested_initially_false(self, token: CancellationToken) -> None:
        # Assert: Verify cancellation is not requested initially
        assert not token.is_cancellation_requested()

    def test_is_cancellation_requested_after_cancel(self, token_source: CancellationTokenSource, token: CancellationToken) -> None:
        # Act: Trigger cancellation
        token_source.cancel()

        # Assert: Verify cancellation is requested
        assert token.is_cancellation_requested()

    def test_throw_if_cancellation_requested_raises_exception(self, token_source: CancellationTokenSource, token: CancellationToken) -> None:
        # Act: Trigger cancellation
        token_source.cancel()

        # Assert: Verify exception is raised
        with pytest.raises(OperationCancelledException):
            token.throw_if_cancellation_requested()

    def test_throw_if_cancellation_requested_no_exception(self, token: CancellationToken) -> None:
        # Assert: Verify no exception is raised when cancellation is not requested
        token.throw_if_cancellation_requested()

    def test_wait_blocks_until_cancellation(self, token_source: CancellationTokenSource, token: CancellationToken) -> None:
        # Arrange: Start a thread to cancel the token after a delay
        def cancel_after_delay() -> None:
            threading.Event().wait(0.1)
            token_source.cancel()

        threading.Thread(target=cancel_after_delay).start()

        # Act: Wait for cancellation
        result: bool = token.wait(timeout=1)

        # Assert: Verify wait returns True after cancellation
        assert result is True

    def test_wait_timeout(self, token: CancellationToken) -> None:
        # Act: Wait with a timeout
        result: bool = token.wait(timeout=0.1)

        # Assert: Verify wait returns False when timeout occurs
        assert result is False