import pytest
from typing import Dict, Type, Any
from unittest.mock import AsyncMock

from repositories.image_repository import ImageRepository
from agents.meme_gen.nodes.node_03_editor import MemeGenEditor
from agents.meme_gen.state import MemeGenState
from integration.configuration_module_factory import ConfigurationModuleFactory
from integration.test_state_factory import TestStateFactory


class TestMemegenEditor:

    @pytest.fixture
    def mocks(self) -> Dict[Type[Any], Any]:
        return {
            ImageRepository: AsyncMock()
        }

    @pytest.fixture
    def node(self, mocks: Dict[Type[Any], Any]) -> MemeGenEditor:
        editor = ConfigurationModuleFactory.build(MemeGenEditor, mocks)
        editor.initialize()
        return editor

    @pytest.mark.asyncio
    async def test_run(self, node: MemeGenEditor, mocks: Dict[Type[Any], Any]):
        # Arrange
        state = MemeGenState()
        state.research = TestStateFactory.get_research()
        state.validation = TestStateFactory.get_validation()
        generation_result = ("image_url", "image_id")
        mocks[ImageRepository].generate_image.return_value = generation_result

        # Act
        final_state = await node.run(state)

        # Assert
        assert final_state.editor
        assert final_state.editor.style
        assert final_state.editor.prompt
        assert final_state.editor.image_url == generation_result[0]
        assert final_state.editor.image_id == generation_result[1]
