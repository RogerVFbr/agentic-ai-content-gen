import pytest

from agents.meme_gen.nodes.node_02_validator import MemeGenTrendValidator
from agents.meme_gen.state import MemeGenState
from integration.configuration_module_factory import ConfigurationModuleFactory
from integration.test_state_factory import TestStateFactory


class TestMemeGenTrendValidator:

    @pytest.fixture
    def node(self) -> MemeGenTrendValidator:
        validator = ConfigurationModuleFactory.build(MemeGenTrendValidator)
        validator.initialize()
        return validator

    @pytest.mark.asyncio
    async def test_run_valid_trends(self, node: MemeGenTrendValidator):
        # Arrange
        state = MemeGenState()
        state.research = TestStateFactory.get_valid_trends()
        state.validation = None

        # Act
        final_state = await node.run(state)

        # Assert
        assert final_state.validation
        assert final_state.validation.primary_topic_status
        assert final_state.validation.primary_topic == "birthday party"
        assert final_state.validation.primary_topic_reason
        assert final_state.validation.secondary_topic_status
        assert final_state.validation.secondary_topic == "mountain hike"
        assert final_state.validation.secondary_topic_reason

    @pytest.mark.asyncio
    async def test_run_invalid_trends(self, node: MemeGenTrendValidator):
        # Arrange
        state = MemeGenState()
        state.research = TestStateFactory.get_invalid_trends()
        state.validation = None

        # Act
        final_state = await node.run(state)

        # Assert
        assert final_state.validation
        assert not final_state.validation.primary_topic_status
        assert final_state.validation.primary_topic == "afghanistan war"
        assert final_state.validation.primary_topic_reason
        assert not final_state.validation.secondary_topic_status
        assert final_state.validation.secondary_topic == "covid 19"
        assert final_state.validation.secondary_topic_reason