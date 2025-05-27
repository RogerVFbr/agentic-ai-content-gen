import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from controllers.controller import MemeGenController


class TestMemeGenController:

    @pytest.fixture
    def mock_dependencies(self, request):
        log_execution_time_patcher = patch('crosscutting.logging.app_logger.AppLogger._log_execution_time', MagicMock())
        log_execution_time_patcher.start()
        request.addfinalizer(log_execution_time_patcher.stop)

        return {
            "agent": AsyncMock(),
            "logger": MagicMock(),
        }

    @pytest.fixture
    def controller(self, mock_dependencies):
        return MemeGenController(**mock_dependencies)

    @pytest.mark.asyncio
    async def test_run_success(self, controller, mock_dependencies):
        # Arrange: Mock the agent's run method
        mock_dependencies["agent"].run.return_value = None

        # Act: Run the controller
        await controller.run({"input_key": "input_value"})

        # Assert: Verify logger and agent calls
        mock_dependencies["logger"].highlight_1.assert_any_call("Running agent ...")
        mock_dependencies["agent"].run.assert_awaited_once_with({"input_key": "input_value"})
        mock_dependencies["logger"].highlight_1.assert_any_call("Agent finished.")

    @pytest.mark.asyncio
    async def test_run_exception(self, controller, mock_dependencies):
        # Arrange: Mock the agent's run method to raise an exception
        mock_dependencies["agent"].run.side_effect = Exception("Test exception")

        # Act: Run the controller
        await controller.run({"input_key": "input_value"})

        # Assert: Verify logger calls and exception handling
        mock_dependencies["logger"].highlight_1.assert_any_call("Running agent ...")
        mock_dependencies["logger"].critical.assert_called_once_with(
            "An error occurred while running the agent: Test exception.",
            exception=mock_dependencies["agent"].run.side_effect,
        )

    @pytest.mark.asyncio
    async def test_terminate(self, controller, mock_dependencies):
        # Act: Terminate the controller
        await controller.terminate()

        # Assert: Verify logger and agent calls
        mock_dependencies["logger"].highlight_1.assert_any_call("Shutting down ...")
        mock_dependencies["agent"].terminate.assert_awaited_once()
        mock_dependencies["logger"].highlight_1.assert_any_call("Shutdown completed.")