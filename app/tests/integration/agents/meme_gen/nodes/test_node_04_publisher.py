import pytest

from agents.meme_gen.nodes.node_04_publisher import MemeGenPublisher
from agents.meme_gen.state import MemeGenState
from integration.configuration_module_factory import ConfigurationModuleFactory
from integration.test_data_factory import TestDataFactory


class TestMemeGenPublisher:

    @pytest.fixture
    def node(self) -> MemeGenPublisher:
        publisher = ConfigurationModuleFactory.build(MemeGenPublisher)
        publisher.initialize()
        return publisher

    @pytest.mark.asyncio
    @pytest.mark.cd_bypass
    async def test_run(self, node: MemeGenPublisher):
        # Arrange
        state = MemeGenState()
        state.research = TestDataFactory.get_research()
        state.validation = TestDataFactory.get_validation()
        state.editor = TestDataFactory.get_edition()

        # Act
        final_state = await node.run(state)

        # Assert
        assert final_state.publisher
        assert not final_state.publisher.status
