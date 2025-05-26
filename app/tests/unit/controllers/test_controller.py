import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.controllers.controller import MemeGenController


class TestMemeGenController:

    @pytest.fixture
    def mock_dependencies(self):
        return {
            "agent": AsyncMock(),
        }

    @pytest.fixture
    def controller(self, mock_dependencies):
        with patch("app.controllers.controller.AppLogger.highlight_1", autospec=True) as mock_highlight_1, \
             patch("app.controllers.controller.AppLogger.critical", autospec=True) as mock_critical, \
             patch("app.controllers.controller.AppLogger.timeit", autospec=True) as mock_timeit, \
             patch("app.controllers.controller.AppLogger._log_execution_time", autospec=True) as mock_log_execution_time:
            mock_timeit.return_value = lambda func: func  # Disable the decorator
            mock_log_execution_time.return_value = None  # Disable logging of execution time
            mock_dependencies["logger"] = MagicMock()
            mock_dependencies["logger"].highlight_1 = mock_highlight_1
            mock_dependencies["logger"].critical = mock_critical
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