import asyncio

import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.meme_gen.agent import MemeGenAgent


class TestMemeGenAgent:

    @pytest.fixture
    def mock_dependencies(self):
        logger = MagicMock()
        graph = AsyncMock()
        return {
            "logger": logger,
            "graph": graph,
        }

    @pytest.fixture
    def agent(self, mock_dependencies):
        return MemeGenAgent(**mock_dependencies)

    # @pytest.mark.asyncio
    # async def test_run_success(self, agent, mock_dependencies):
    #     # Arrange: Mock the graph's build and astream methods
    #     mock_dependencies["graph"].build.return_value = AsyncMock()
    #     mock_dependencies["graph"].build.return_value.astream.return_value = AsyncMock()
    #     mock_dependencies["graph"].build.return_value.astream.return_value.__aiter__ = lambda: iter([
    #         {"step_1": "executed"},
    #         {"step_2": "executed"},
    #     ])
    #
    #     # Act: Run the agent
    #     await agent.run({"input_key": "input_value"})
    #
    #     # Assert: Verify the graph and logger calls
    #     mock_dependencies["graph"].build.assert_awaited_once()
    #     mock_dependencies["logger"].info.assert_any_call("Graph: 'step_1' node executed.")
    #     mock_dependencies["logger"].info.assert_any_call("Graph: 'step_2' node executed.")

    @pytest.mark.asyncio
    async def test_run_cancelled(self, agent, mock_dependencies):
        # Arrange: Mock the graph's build method to raise CancelledError
        mock_dependencies["graph"].build.side_effect = asyncio.CancelledError

        # Act: Run the agent
        await agent.run({"input_key": "input_value"})

        # Assert: Verify the logger warning
        mock_dependencies["logger"].warn.assert_called_once_with("Agent execution cancelled.")

    @pytest.mark.asyncio
    async def test_terminate(self, agent, mock_dependencies):
        # Act: Terminate the agent
        await agent.terminate()

        # Assert: Verify the graph's terminate method was called
        mock_dependencies["graph"].terminate.assert_awaited_once()