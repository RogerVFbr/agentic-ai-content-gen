import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.agents.meme_gen.graph import MemeGenGraphBuilder


class TestMemeGenGraph:

    @pytest.fixture
    def mock_dependencies(self):
        return {
            "logger": MagicMock(),
            "initializer": MagicMock(),
            "researcher": MagicMock(),
            "validator": MagicMock(),
            "editor": MagicMock(),
            "publisher": MagicMock(),
            "failure": MagicMock(),
            "success": MagicMock(),
        }

    @pytest.mark.asyncio
    async def test_initialize_success(self, mock_dependencies):
        # Arrange: Create a MemeGenGraphBuilder instance and mock required methods
        graph = MemeGenGraphBuilder(**mock_dependencies)
        with patch.object(graph, "_initialize_checkpointer", new_callable=AsyncMock) as mock_initialize_checkpointer:
            # Act: Call the initialize method
            await graph.initialize()

            # Assert: Verify that the checkpointer is initialized and nodes are initialized
            mock_initialize_checkpointer.assert_awaited_once()
            mock_dependencies["researcher"].initialize.assert_called_once()
            mock_dependencies["validator"].initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_checkpointer(self, mock_dependencies):
        # Arrange: Create a MemeGenGraph instance and mock required methods
        graph = MemeGenGraphBuilder(**mock_dependencies)

        with patch("os.makedirs") as mock_makedirs, \
                patch("os.path.exists", return_value=False), \
                patch("aiosqlite.connect", new_callable=AsyncMock) as mock_connect:

            # Act: Call the _initialize_checkpointer method
            await graph._initialize_checkpointer()

            # Assert: Verify that the directory is created and SQLite connection is initialized
            mock_makedirs.assert_called_once_with(graph.memory_file.rsplit("/", 1)[0])
            mock_connect.assert_called_once_with(graph.memory_file)

    @pytest.mark.asyncio
    async def test_build(self, mock_dependencies):
        # Arrange: Create a MemeGenGraph instance and mock required methods
        graph = MemeGenGraphBuilder(**mock_dependencies)

        with patch("app.agents.meme_gen.graph.StateGraph") as MockStateGraph, \
                patch.object(graph, "_save_graph_image", new_callable=AsyncMock) as mock_save_image:

            mock_builder = MockStateGraph.return_value
            try:

                # Act: Call the build method
                await graph.build()

                # Assert: Verify that nodes, edges, and conditional edges are added, and the graph image is saved
                assert mock_builder.add_node.call_count == 7
                assert mock_builder.add_edge.call_count == 3
                assert mock_builder.add_conditional_edges.call_count == 4
                mock_save_image.assert_called_once()
            finally:

                # Cleanup: Ensure any async tasks or resources are properly closed
                if graph.conn:
                    await graph.terminate()

    def test_save_graph_image(self, mock_dependencies):
        # Arrange: Create a MemeGenGraph instance and mock required methods
        graph = MemeGenGraphBuilder(**mock_dependencies)
        mock_graph = MagicMock()
        with patch("os.makedirs") as mock_makedirs, \
                patch("os.path.exists", return_value=False), \
                patch("builtins.open", new_callable=MagicMock) as mock_open:

            # Act: Call the _save_graph_image method
            graph._save_graph_image(mock_graph)

            # Assert: Verify that the directory is created and the graph image is saved
            mock_makedirs.assert_called_once_with(graph.memory_file.rsplit("/", 1)[0])
            mock_open.assert_called_once_with(graph.memory_file.replace("sql_memory.db", "memegen_graph.png"), "wb")

    @pytest.mark.asyncio
    async def test_terminate(self, mock_dependencies):
        # Arrange: Create a MemeGenGraph instance and mock the SQLite connection
        graph = MemeGenGraphBuilder(**mock_dependencies)
        mock_conn = AsyncMock()
        graph.conn = mock_conn

        # Act: Call the terminate method
        await graph.terminate()
        
        # Assert: Verify that the connection is committed, closed, and the logger records the termination
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
        mock_dependencies["logger"].info.assert_called_once_with("Checkpointer database connection terminated.")