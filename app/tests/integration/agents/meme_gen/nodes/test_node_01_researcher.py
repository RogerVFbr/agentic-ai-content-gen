import pytest

from agents.meme_gen.nodes.node_01_researcher import MemeGenTrendResearcher
from agents.meme_gen.state import MemeGenState
from integration.configuration_module_factory import ConfigurationModuleFactory


class TestMemeGenTrendResearcher:

    @pytest.fixture
    def node(self) -> MemeGenTrendResearcher:
        researcher = ConfigurationModuleFactory.build(MemeGenTrendResearcher)
        researcher.initialize()
        return researcher

    @pytest.mark.asyncio
    async def test_run(self, node: MemeGenTrendResearcher):
        try:
            _ = await node.run(MemeGenState())
        except Exception as e:
            pytest.fail(f"Unexpected exception raised: {e}")
        assert True

