import pytest

from agents.meme_gen.nodes.node_05_failure import MemeGenFailure
from agents.meme_gen.nodes.node_06_success import MemeGenSuccess
from agents.meme_gen.state import MemeGenState
from integration.configuration_module_factory import ConfigurationModuleFactory


class TestMemeGenSuccess:

    @pytest.fixture
    def node(self) -> MemeGenSuccess:
        success = ConfigurationModuleFactory.build(MemeGenSuccess)
        return success

    @pytest.mark.asyncio
    async def test_run(self, node: MemeGenFailure):
        # Arrange
        state = MemeGenState()

        # Act
        final_state = await node.run(state)

        # Assert
        assert final_state == state