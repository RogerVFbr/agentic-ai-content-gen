import pytest
from typing import Dict, Type, Any
from unittest.mock import AsyncMock

from agents.meme_gen.nodes.node_01_researcher import MemeGenTrendResearcher
from agents.meme_gen.state import MemeGenState
from integration.configuration_module_factory import ConfigurationModuleFactory
from repositories.web_trends_repository import WebTrendsRepository


class TestMemeGenTrendResearcher:

    @pytest.fixture
    def mocks(self) -> Dict[Type[Any], Any]:
        return {
            WebTrendsRepository: AsyncMock()
        }

    @pytest.fixture
    def node(self, mocks: Dict[Type[Any], Any]) -> MemeGenTrendResearcher:
        researcher = ConfigurationModuleFactory.build(MemeGenTrendResearcher, mocks)
        researcher.initialize()
        return researcher

    @pytest.mark.asyncio
    async def test_run(self, node: MemeGenTrendResearcher, mocks: Dict[Type[Any], Any]):
        # Arrange
        state = MemeGenState()
        api_results = self._get_repo_mock_results()
        mocks[WebTrendsRepository].get_trending_now.return_value = api_results

        # Act
        final_state = await node.run(state)

        # Assert
        assert final_state.research
        assert final_state.research.primary_topic == "birthday party" or final_state.research.primary_topic == "mountain hike"
        assert final_state.research.secondary_topic == "birthday party" or final_state.research.secondary_topic == "mountain hike"
        assert final_state.research.primary_topic != final_state.research.secondary_topic
        assert final_state.research.tool_call_status
        assert final_state.research.tool_call_reason
        assert final_state.research.combined_joke
        assert final_state.research.primary_topic_reason
        assert final_state.research.secondary_topic_reason
        assert final_state.research.primary_topic_facts
        assert final_state.research.secondary_topic_facts
        assert len(final_state.research.full_topics_list) == len(api_results)

    @staticmethod
    def _get_repo_mock_results():
        return [
            {
                "trend_name": "afganistan war",
                "trending_associated_keywords": ["war", "conflict", "troops"],
                "number_of_searches": 10000,
                "volume_growth_pct": 1000,
                "categories": ["Geopolitics"],
            },
            {
                "trend_name": "covid 19",
                "trending_associated_keywords": ["disease", "pandemic"],
                "number_of_searches": 9990,
                "volume_growth_pct": 1000,
                "categories": ["Health"],
            },
            {
                "trend_name": "birthday party",
                "trending_associated_keywords": ["birthday cake", "candles"],
                "number_of_searches": 100,
                "volume_growth_pct": 10,
                "categories": ["Technology"]
            },
            {
                "trend_name": "mountain hike",
                "trending_associated_keywords": ["nature", "sight seeing"],
                "number_of_searches": 200,
                "volume_growth_pct": 20,
                "categories": ["Sports"]
            }
        ]

