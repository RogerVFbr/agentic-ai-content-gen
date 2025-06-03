import pytest
from typing import Union

from agents.meme_gen.nodes.node_00_initializer import MemeGenInitializer
from agents.meme_gen.state import MemeGenState
from integration.configuration_module_factory import ConfigurationModuleFactory


class TestMemeGenInitializer:

    @pytest.fixture
    def node(self) -> MemeGenInitializer:
        return ConfigurationModuleFactory.build(MemeGenInitializer)

    @pytest.mark.asyncio
    async def test_run(self, node: MemeGenInitializer):
        # Arrange
        state = MemeGenState()

        # Act
        final_state = await node.run(state)

        # Assert
        assert final_state.trend_research is None
        assert final_state.trend_research_validation is None

