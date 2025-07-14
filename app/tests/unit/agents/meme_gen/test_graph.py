import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from agents.meme_gen.graph import MemeGenGraphBuilder


class TestMemeGenGraphBuilder:

    @pytest.fixture
    def mock_dependencies(self):
        return {
            "logger": MagicMock(),
            "initializer": AsyncMock(),
            "researcher": MagicMock(),
            "validator": MagicMock(),
            "editor": MagicMock(),
            "publisher": MagicMock(),
            "failure": MagicMock(),
            "success": MagicMock(),
            "terminate": AsyncMock(),
        }

    @pytest.fixture
    def builder(self, mock_dependencies) -> MemeGenGraphBuilder:
        return MemeGenGraphBuilder(**mock_dependencies)

    @pytest.mark.asyncio
    async def test_initialize_success(self, builder: MemeGenGraphBuilder, mock_dependencies):
        # Act: Call the initialize method
        await builder.initialize()

        # Assert: Verify that the checkpointer is initialized and nodes are initialized
        mock_dependencies["researcher"].initialize.assert_called_once()
        mock_dependencies["validator"].initialize.assert_called_once()
        mock_dependencies["editor"].initialize.assert_called_once()
        mock_dependencies["initializer"].initialize.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_build(self, builder: MemeGenGraphBuilder, mock_dependencies):
        # Arrange: Mock required methods
        with patch("agents.meme_gen.graph.StateGraph") as MockStateGraph, \
                patch.object(builder, "_save_graph_image", new_callable=AsyncMock) as mock_save_image:

            mock_builder = MockStateGraph.return_value

            # Act: Call the build method
            await builder.build()

            # Assert: Verify that nodes, edges, and conditional edges are added, and the graph image is saved
            assert mock_builder.add_node.call_count == 8
            assert mock_builder.add_edge.call_count == 4
            assert mock_builder.add_conditional_edges.call_count == 4
            mock_save_image.assert_called_once()


    def test_save_graph_image(self, builder: MemeGenGraphBuilder, mock_dependencies):
        # Arrange: Mock required methods
        mock_graph = MagicMock()
        with patch("os.makedirs") as mock_makedirs, \
                patch("os.path.exists", return_value=False), \
                patch("builtins.open", new_callable=MagicMock) as mock_open:

            # Act: Call the _save_graph_image method
            builder._save_graph_image(mock_graph)

            # Assert: Verify that the directory is created and the graph image is saved
            mock_makedirs.assert_called_once()
            mock_open.assert_called_once()

    @pytest.mark.asyncio
    async def test_terminate(self, builder: MemeGenGraphBuilder, mock_dependencies):
        # Act: Call the terminate method
        await builder.terminate()
        
        # Assert: Verify termination
        mock_dependencies["terminate"].terminate.assert_awaited_once()
