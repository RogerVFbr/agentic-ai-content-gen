import asyncio

import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.meme_gen.agent import MemeGenAgent


class AsyncIterator:
    def __init__(self, seq):
        self.iter = iter(seq)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration


class TestMemeGenAgent:

    @pytest.fixture
    def mock_dependencies(self):
        return {
            "logger": MagicMock(),
            "builder": AsyncMock(),
        }

    @pytest.mark.asyncio
    async def test_initialize_success(self, agent, mock_dependencies):
        # Arrange: Mock the builder's initialize and build methods
        mock_dependencies["builder"].initialize.return_value = None
        mock_dependencies["builder"].build.return_value = MagicMock()

        # Act: Initialize the agent
        await agent.initialize()

        # Assert: Verify builder calls and graph assignment
        mock_dependencies["builder"].initialize.assert_awaited_once()
        mock_dependencies["builder"].build.assert_awaited_once()
        assert agent.graph is not None

    @pytest.fixture
    def agent(self, mock_dependencies):
        agent = MemeGenAgent(**mock_dependencies)
        return agent

    @pytest.mark.asyncio
    async def test_run_success(self, agent, mock_dependencies):
        # Arrange: Mock the graph's build and astream methods
        mock_graph_instance = MagicMock()
        mock_graph_instance.astream.return_value = AsyncIterator([
            {"step_1": "executed"},
            {"step_2": "executed"},
        ])
        mock_dependencies["builder"].build.return_value = mock_graph_instance

        # Act: Run the agent
        await agent.initialize()
        await agent.run({"input_key": "input_value"})

        # Assert: Verify the graph and logger calls
        mock_dependencies["builder"].build.assert_awaited_once()
        mock_dependencies["logger"].info.assert_any_call("Graph: 'step_1' node executed.")
        mock_dependencies["logger"].info.assert_any_call("Graph: 'step_2' node executed.")

    @pytest.mark.asyncio
    async def test_run_cancelled(self, agent, mock_dependencies):
        # Arrange: Mock the graph's build method to raise CancelledError
        mock_graph_instance = MagicMock()
        mock_graph_instance.astream.side_effect = asyncio.CancelledError
        mock_dependencies["builder"].build.return_value = mock_graph_instance

        # Act: Run the agent
        await agent.initialize()
        await agent.run({"input_key": "input_value"})

        # Assert: Verify the logger warning
        mock_dependencies["logger"].warn.assert_called_once_with("Agent execution cancelled.")

    @pytest.mark.asyncio
    async def test_terminate(self, agent, mock_dependencies):
        # Act: Terminate the agent
        await agent.terminate()

        # Assert: Verify the graph's terminate method was called
        mock_dependencies["builder"].terminate.assert_awaited_once()