from unittest.mock import AsyncMock

from typing import Any, Type, Dict

import pytest

from integration.configuration_module_factory import ConfigurationModuleFactory
from repositories.used_topics_repository import UsedTopicsRepository
from agents.meme_gen.nodes.node_00_initializer import MemeGenInitializer
from agents.meme_gen.state import MemeGenState


class TestMemeGenInitializer:

    @pytest.fixture
    def mocks(self) -> Dict[Type[Any], Any]:
        return {
            UsedTopicsRepository: AsyncMock()
        }

    @pytest.fixture
    def node(self, mocks: Dict[Type[Any], Any]) -> MemeGenInitializer:
        return ConfigurationModuleFactory.build(MemeGenInitializer, mocks)

    @pytest.mark.asyncio
    async def test_run(self, node: MemeGenInitializer, mocks: Dict[Type[Any], Any]):
        # Arrange
        state = MemeGenState()
        used_topics = ["Topic1", "Topic2", "Topic3"]
        mocks[UsedTopicsRepository].get_all_topic_names.return_value = used_topics

        # Act
        final_state = await node.run(state)

        # Assert
        assert not final_state.research
        assert not final_state.validation
        assert final_state.prior_topics == set(used_topics)

