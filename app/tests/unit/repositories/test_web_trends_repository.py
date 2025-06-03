import pytest
from unittest.mock import AsyncMock, MagicMock
from repositories.web_trends_repository import WebTrendsRepository


class TestWebTrendsRepository:

    @pytest.fixture
    def mock_dependencies(self):
        logger = MagicMock()
        client = AsyncMock()
        return {
            "logger": logger,
            "client": client,
        }

    @pytest.fixture
    def repository(self, mock_dependencies):
        return WebTrendsRepository(**mock_dependencies)

    @pytest.mark.asyncio
    async def test_get_trending_now_initializes_model(self, repository, mock_dependencies):
        # Arrange: Ensure the model is not initialized
        repository.model = None
        mock_dependencies["client"].get_trending_now.return_value = []

        # Act: Call the method
        await repository.get_trending_now(country="US", exclusion_list=[], limit=10)

        # Assert: Verify the model was initialized
        assert repository.model is not None

    @pytest.mark.asyncio
    async def test_get_trending_now_excludes_categories(self, repository, mock_dependencies):
        # Arrange: Mock client response with excluded categories
        mock_dependencies["client"].get_trending_now.return_value = [
            MagicMock(keyword="Trend1", trend_keywords=[], volume=100, volume_growth_pct=10, topic_names=["Sports"]),
            MagicMock(keyword="Trend2", trend_keywords=[], volume=200, volume_growth_pct=20, topic_names=["Technology"]),
        ]

        # Act: Call the method
        result = await repository.get_trending_now(country="US", exclusion_list=[], limit=10)

        # Assert: Verify excluded categories are filtered out
        assert len(result) == 1
        assert result[0]["trend_name"] == "Trend2"

    @pytest.mark.asyncio
    async def test_get_trending_now_excludes_similar_keywords(self, repository, mock_dependencies):
        # Arrange: Mock client response with similar keywords
        mock_dependencies["client"].get_trending_now.return_value = [
            MagicMock(keyword="Trend1", trend_keywords=[], volume=100, volume_growth_pct=10, topic_names=[]),
            MagicMock(keyword="Trend2", trend_keywords=[], volume=200, volume_growth_pct=20, topic_names=[]),
        ]
        exclusion_list = ["Trend1"]

        # Act: Call the method
        result = await repository.get_trending_now(country="US", exclusion_list=exclusion_list, limit=10)

        # Assert: Verify similar keywords are filtered out
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_trending_now_excludes_semantically_similar_keywords(self, repository, mock_dependencies):
        # Arrange: Mock client response with similar keywords
        mock_dependencies["client"].get_trending_now.return_value = [
            MagicMock(keyword="the president of United States of America", trend_keywords=[], volume=100, volume_growth_pct=10, topic_names=[]),
            MagicMock(keyword="US president", trend_keywords=[], volume=200, volume_growth_pct=20, topic_names=[]),
        ]
        exclusion_list = ["the president of United States"]

        # Act: Call the method
        result = await repository.get_trending_now(country="US", exclusion_list=exclusion_list, limit=10)

        # Assert: Verify similar keywords are filtered out
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_trending_now_limits_results(self, repository, mock_dependencies):
        # Arrange: Mock client response with multiple trends
        mock_dependencies["client"].get_trending_now.return_value = [
            MagicMock(keyword=f"Trend{i}", trend_keywords=[], volume=100, volume_growth_pct=10, topic_names=[])
            for i in range(15)
        ]

        # Act: Call the method with a limit
        result = await repository.get_trending_now(country="US", exclusion_list=[], limit=10)

        # Assert: Verify the result is limited to the specified number
        assert len(result) == 10
        assert result[0]["trend_name"] == "Trend0"
        assert result[-1]["trend_name"] == "Trend9"