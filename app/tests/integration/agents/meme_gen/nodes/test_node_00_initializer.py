import pytest
from typing import Union

from agents.meme_gen.nodes.node_00_initializer import MemeGenInitializer
from agents.meme_gen.state import MemeGenState
from integration.configuration_module_factory import ConfigurationModuleFactory


class TestMemeGenInitializer:

    @pytest.fixture
    def node(self) -> Union[MemeGenInitializer, None]:
        return ConfigurationModuleFactory.build(MemeGenInitializer)

    @pytest.mark.asyncio
    async def test_run(self, node: MemeGenInitializer):
        try:
            await node.run(MemeGenState())
        except Exception as e:
            pytest.fail(f"Unexpected exception raised: {e}")
        assert True

