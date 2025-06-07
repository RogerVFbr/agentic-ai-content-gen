import asyncio
import pytest
import threading
from unittest.mock import AsyncMock

from crosscutting.background_service.one_shot_background_service import OneShotBackgroundService


class MockBackgroundService(OneShotBackgroundService):
    async def start(self, cancellation_token, input=None):
        await asyncio.sleep(0.5)

    async def stop(self, cancellation_token, input=None):
        pass

    async def on_initialize(self):
        pass

    async def on_terminate(self):
        pass


class TestOneShotBackgroundService:

    @pytest.fixture
    def mock_service(self):
        service = MockBackgroundService()
        service.start = AsyncMock(wraps=service.start)
        service.stop = AsyncMock()
        service.on_initialize = AsyncMock()
        service.on_terminate = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_run_success(self, mock_service: MockBackgroundService):
        # Act: Run the service
        await mock_service.run(input="test_input")

        # Assert: Verify lifecycle methods were called
        mock_service.start.assert_awaited_once_with(mock_service._cancellation_token_source.token, "test_input")
        mock_service.stop.assert_awaited_once()
        mock_service.on_initialize.assert_awaited_once()
        mock_service.on_terminate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_run_exception_handling(self, mock_service: MockBackgroundService):
        # Arrange: Mock the start method to throw an exception
        mock_service.start.side_effect = Exception("Test exception")

        # Act: Run the service
        with pytest.raises(Exception, match="Test exception"):
            await mock_service.run(input="test_input")

        # Assert: Verify lifecycle methods were called despite the exception
        mock_service.stop.assert_awaited_once()
        mock_service.on_terminate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_run_cancellation(self, mock_service: MockBackgroundService):
        # Arrange: Define the shutdown logic
        def emulate_cancellation():
            asyncio.run(asyncio.sleep(0.2))
            mock_service._set_shutdown_event()

        # Run the shutdown logic in a separate thread
        shutdown_thread = threading.Thread(target=emulate_cancellation)
        shutdown_thread.start()

        # Act: Launch the service
        await mock_service.run(input="test_input")
        shutdown_thread.join()

        # Assert: Verify run cancellation behavior
        assert mock_service._cancellation_token_source.token.is_cancellation_requested()
        mock_service.on_terminate.assert_awaited_once()
        mock_service.stop.assert_awaited_once()