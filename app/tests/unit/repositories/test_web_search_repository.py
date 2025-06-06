import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from configurations.configs import WebSearchClient
from repositories.web_search_repository import WebSearchRepository


class TestWebSearchRepository:

    @pytest.fixture
    def mock_dependencies(self):
        configs = MagicMock()
        configs.web_search.cache_path = "/mock/cache/path"
        configs.web_search.cache_ttl_minutes = 60
        configs.web_search.quota_per_node = 5
        configs.web_search.client = WebSearchClient.Tavily
        return {
            "logger": MagicMock(),
            "configs": configs,
            "tavily_client": AsyncMock(),
            "serper_dev_client": AsyncMock(),
        }

    @pytest.fixture
    def repository(self, mock_dependencies):
        return WebSearchRepository(**mock_dependencies)

    @pytest.mark.asyncio
    async def test_search_cache_hit(self, repository, mock_dependencies):
        # Arrange: Set up the repository with a mocked cache and a predefined cache hit
        repository.cache = MagicMock()
        repository.cache.search.return_value = {
            "result": "cached_result",
            "match_query": "query",
            "score": 0.9,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Act: Perform the search operation
        result = await repository.search("node_01", "query")

        # Assert: Verify the result and ensure the cache was queried
        assert result == "cached_result"
        repository.cache.search.assert_called_once_with("query")
        mock_dependencies["logger"].debug.assert_called()

    @pytest.mark.asyncio
    async def test_search_quota_exceeded(self, repository, mock_dependencies):
        # Arrange: Set the quota usage to exceed the limit
        repository.quota_usage["node_01"] = 5

        # Act: Perform the search operation
        result = await repository.search("node_01", "query")

        # Assert: Verify the error message and logger call
        assert result == {
            "error": "Client quota exceeded",
            "message": "You have reached your application level search quota of 5 searches.",
        }
        mock_dependencies["logger"].warn.assert_called()

    @pytest.mark.asyncio
    async def test_search_tavily_client(self, repository, mock_dependencies):
        # Arrange: Set up the repository to use the Tavily client
        repository.cache = MagicMock()
        repository.cache.search.return_value = None
        mock_dependencies["configs"].web_search.client = WebSearchClient.Tavily
        mock_dependencies["tavily_client"].search.return_value = "tavily_result"

        # Act: Perform the search operation
        result = await repository.search("node_01", "query")

        # Assert: Verify the result, cache storage, and client call
        assert result == "tavily_result"
        repository.cache.store.assert_called_once_with("query", "tavily_result")
        mock_dependencies["tavily_client"].search.assert_awaited_once_with(query="query")
        mock_dependencies["logger"].debug.assert_called()

    @pytest.mark.asyncio
    async def test_search_serper_dev_client(self, repository, mock_dependencies):
        # Arrange: Set up the repository to use the SerperDev client
        repository.cache = MagicMock()
        repository.cache.search.return_value = None
        mock_dependencies["configs"].web_search.client = WebSearchClient.SerperDev
        mock_dependencies["serper_dev_client"].search.return_value = "serper_result"

        # Act: Perform the search operation
        result = await repository.search("node_01", "query")

        # Assert: Verify the result, cache storage, and client call
        assert result == "serper_result"
        repository.cache.store.assert_called_once_with("query", "serper_result")
        mock_dependencies["serper_dev_client"].search.assert_awaited_once_with(query="query")
        mock_dependencies["logger"].debug.assert_called()

    @pytest.mark.asyncio
    async def test_search_unknown_client(self, repository, mock_dependencies):
        # Arrange: Set up the repository with an unknown client
        repository.cache = MagicMock()
        repository.cache.search.return_value = None
        mock_dependencies["configs"].web_search.client = "UnknownClient"

        # Act & Assert: Verify that an exception is raised for the unknown client
        with pytest.raises(Exception, match="Unknown client 'UnknownClient'."):
            await repository.search("node_01", "query")

    def test_reset_quota(self, repository):
        # Arrange: Set the quota usage for a node
        repository.quota_usage["node_01"] = 5

        # Act: Reset the quota for the node
        repository.reset_quota("node_01")

        # Assert: Verify that the quota usage is reset
        assert repository.quota_usage["node_01"] == 0

    def test_save(self, repository, mock_dependencies):
        # Arrange: Set up the repository with usage and cache hits
        repository.cache = MagicMock()
        repository.usage = 10
        repository.cache_hits = 3

        # Act: Save the repository state
        repository.save()

        # Assert: Verify the logger calls and cache save
        mock_dependencies["logger"].info.assert_any_call("Web search session usage: 10 (+3 cache hits).")
        repository.cache.save.assert_called_once()
        mock_dependencies["logger"].info.assert_any_call("Web search cache flushed.")