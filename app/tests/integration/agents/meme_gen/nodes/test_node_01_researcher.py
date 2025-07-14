import pytest
from typing import Dict, Type, Any
from unittest.mock import AsyncMock

from agents.meme_gen.nodes.node_01_researcher import MemeGenTrendResearcher
from agents.meme_gen.state import MemeGenState
from integration.configuration_module_factory import ConfigurationModuleFactory
from integration.test_data_factory import TestDataFactory
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
    @pytest.mark.cd_bypass
    async def test_run(self, node: MemeGenTrendResearcher, mocks: Dict[Type[Any], Any]):
        # Arrange
        state = MemeGenState()
        api_results = TestDataFactory.get_web_trends_mock_results()
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