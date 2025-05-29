import pytest
from typing import Union

from agents.meme_gen.nodes.node_00_initializer import MemeGenInitializer
from agents.meme_gen.state import MemeGenState
from configurations.configuration_module import ConfigurationModule
from configurations.di_container import DiContainer
from configurations.di_services import MemeGenDi
from crosscutting.logging.app_logger import AppLogger


class TestMemeGenInitializer:

    @pytest.fixture
    def node(self) -> Union[MemeGenInitializer, None]:
        AppLogger.CONFIGS.is_structured = False
        module = ConfigurationModule()
        pre_instantiated = MemeGenDi.get_pre_instantiated()
        service_collection = MemeGenDi.get_service_collection()
        if module.initialize(pre_instantiated, service_collection):
            return DiContainer.get(MemeGenInitializer)
        return None

    @pytest.mark.asyncio
    async def test_run(self, node: MemeGenInitializer):
        try:
            await node.run(MemeGenState())
        except Exception as e:
            pytest.fail(f"Unexpected exception raised: {e}")
        assert True

