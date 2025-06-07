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
    async def test_initialize_success(self, controller, mock_dependencies):
        # Arrange: Mock the agent's initialize method
        mock_dependencies["agent"].initialize.return_value = None

        # Act: Initialize the controller
        await controller.initialize()

        # Assert: Verify logger and agent calls
        mock_dependencies["logger"].info.assert_called_once_with("Initialization requested ...")
        mock_dependencies["agent"].initialize.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_initialize_exception(self, controller, mock_dependencies):
        # Arrange: Mock the agent's initialize method to raise an exception
        mock_dependencies["agent"].initialize.side_effect = Exception("Initialization error")

        # Act: Initialize the controller
        with pytest.raises(Exception, match="Initialization error"):
            await controller.initialize()

        # Assert: Verify logger calls and exception handling
        mock_dependencies["logger"].info.assert_called_once_with("Initialization requested ...")
        mock_dependencies["logger"].critical.assert_called_once_with(
            "An error occurred while running the agent: Initialization error.",
            exception=mock_dependencies["agent"].initialize.side_effect,
        )

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
        with pytest.raises(Exception, match="Test exception"):
            await controller.run({"input_key": "input_value"})

        # Assert: Verify logger calls and exception handling
        mock_dependencies["logger"].highlight_1.assert_any_call("Running agent ...")
        mock_dependencies["logger"].critical.assert_called_once_with(
            "An error occurred while running the agent: Test exception.",
            exception=mock_dependencies["agent"].run.side_effect,
        )

    @pytest.mark.asyncio
    async def test_terminate_success(self, controller, mock_dependencies):
        # Arrange: Mock the agent's terminate method
        mock_dependencies["agent"].terminate.return_value = None

        # Act: Terminate the controller
        await controller.terminate()

        # Assert: Verify logger and agent calls
        mock_dependencies["logger"].highlight_1.assert_any_call("Shutting down ...")
        mock_dependencies["agent"].terminate.assert_awaited_once()
        mock_dependencies["logger"].highlight_1.assert_any_call("Shutdown completed.")

    @pytest.mark.asyncio
    async def test_terminate_exception(self, controller, mock_dependencies):
        # Arrange: Mock the agent's terminate method to raise an exception
        mock_dependencies["agent"].terminate.side_effect = Exception("Termination error")

        # Act: Terminate the controller
        with pytest.raises(Exception, match="Termination error"):
            await controller.terminate()

        # Assert: Verify logger calls and exception handling
        mock_dependencies["logger"].highlight_1.assert_any_call("Shutting down ...")
        mock_dependencies["logger"].critical.assert_called_once_with(
            "Unable to gracefully shutdown the application: Termination error.",
            exception=mock_dependencies["agent"].terminate.side_effect,
        )