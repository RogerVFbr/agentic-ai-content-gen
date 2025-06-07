import threading

import asyncio
import pytest
from unittest.mock import AsyncMock

from crosscutting.background_service.multi_shot_background_service import MultiShotBackgroundService


class MockMultiShotBackgroundService(MultiShotBackgroundService):
    async def start(self, cancellation_token, input=None):
        await asyncio.sleep(0.5)

    async def stop(self, cancellation_token, input=None):
        pass

    async def on_initialize(self):
        pass

    async def on_terminate(self):
        pass


class TestMultiShotBackgroundService:

    @pytest.fixture
    def mock_service(self):
        service = MockMultiShotBackgroundService()
        service.start = AsyncMock(wraps=service.start)
        service.stop = AsyncMock()
        service.on_initialize = AsyncMock()
        service.on_terminate = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_run_initialization(self, mock_service):
        # Act: Run the service for the first time
        await mock_service.run(input="test_input")

        # Assert: Verify on_initialize is called only once
        mock_service.on_initialize.assert_awaited_once()
        mock_service.start.assert_awaited_once_with(mock_service._cancellation_token_source.token, "test_input")
        mock_service.stop.assert_not_awaited()
        mock_service.on_terminate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_run_multiple_times(self, mock_service):
        # Act: Run the service multiple times
        await mock_service.run(input="test_input_1")
        await mock_service.run(input="test_input_2")

        # Assert: Verify on_initialize is called only once and start is called twice
        mock_service.on_initialize.assert_awaited_once()
        assert mock_service.start.call_count == 2
        mock_service.stop.assert_not_awaited()
        mock_service.on_terminate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_run_with_exception(self, mock_service):
        # Arrange: Mock the start method to throw an exception
        mock_service.start.side_effect = Exception("Test exception")

        # Act: Run the service and expect an exception
        with pytest.raises(Exception, match="Test exception"):
            await mock_service.run(input="test_input")

        # Assert: Verify stop is called after the exception
        mock_service.stop.assert_awaited_once_with(mock_service._cancellation_token_source.token, "test_input")
        assert not mock_service._cancellation_token_source.token.is_cancellation_requested()
        mock_service.on_initialize.assert_awaited_once()
        mock_service.on_terminate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_run_cancellation_while_run_inflight(self, mock_service: MockMultiShotBackgroundService):
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

    @pytest.mark.asyncio
    async def test_run_cancellation_while_idle_and_pristine(self, mock_service: MockMultiShotBackgroundService):
        # Arrange: Define the shutdown logic
        def emulate_cancellation():
            mock_service._set_shutdown_event()

        shutdown_thread = threading.Thread(target=emulate_cancellation)

        # Act: Emulate cancellation
        shutdown_thread.start()
        shutdown_thread.join()

        # Assert: Verify run cancellation behavior
        mock_service.start.assert_not_awaited()
        assert not mock_service._cancellation_token_source.token.is_cancellation_requested()
        mock_service.on_terminate.assert_awaited_once()
        mock_service.stop.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_run_cancellation_while_idle_and_dirty(self, mock_service: MockMultiShotBackgroundService):
        # Arrange: Define the shutdown logic
        def emulate_cancellation():
            mock_service._set_shutdown_event()

        shutdown_thread = threading.Thread(target=emulate_cancellation)

        # Act: Emulate cancellation
        await mock_service.run(input="test_input")
        shutdown_thread.start()
        shutdown_thread.join()

        # Assert: Verify run cancellation behavior
        mock_service.start.assert_awaited_once()
        assert not mock_service._cancellation_token_source.token.is_cancellation_requested()
        mock_service.on_terminate.assert_awaited_once()
        mock_service.stop.assert_awaited_once()