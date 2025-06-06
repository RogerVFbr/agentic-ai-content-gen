# python
import asyncio
import pytest
import threading
from unittest.mock import AsyncMock

from crosscutting.one_shot_background_service import OneShotBackgroundService


class MockBackgroundService(OneShotBackgroundService):
    async def start(self, cancellation_token, input=None):
        await asyncio.sleep(0.5)

    async def stop(self):
        pass

    async def on_terminate(self):
        pass


class TestOneShotBackgroundService:

    @pytest.fixture
    def mock_service(self):
        service = MockBackgroundService()
        service.start = AsyncMock(wraps=service.start)
        service.stop = AsyncMock()
        service.on_terminate = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_run_sucess(self, mock_service):
        # Act: Run the service
        await mock_service.run(input="test_input")

        # Assert: Verify lifecycle methods were called
        mock_service.start.assert_awaited_once_with(mock_service._cancellation_token_source.token, "test_input")
        mock_service.stop.assert_awaited_once()
        mock_service.on_terminate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_run_exception_handling(self, mock_service):
        # Arrange: Mock the start method to throw an exception
        mock_service.start.side_effect = Exception("Test exception")

        # Act: Run the service
        with pytest.raises(Exception, match="Test exception"):
            await mock_service.run(input="test_input")

        # Assert: Verify lifecycle methods were called despite the exception
        mock_service.stop.assert_awaited_once()
        mock_service.on_terminate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_run_cancellation(self, mock_service):
        # Arrange: Define the shutdown logic
        def emulate_shutdown():
            asyncio.run(asyncio.sleep(0.2))
            mock_service._set_shutdown_event()

        # Run the shutdown logic in a separate thread
        shutdown_thread = threading.Thread(target=emulate_shutdown)
        shutdown_thread.start()

        # Act: Launch the service
        await mock_service.run(input="test_input")
        shutdown_thread.join()

        # Assert: Verify run cancellation behavior
        assert mock_service._cancellation_token_source.token.is_cancellation_requested()
        mock_service.on_terminate.assert_awaited_once()
        mock_service.stop.assert_awaited_once()