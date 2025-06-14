import pytest

from agents.meme_gen.nodes.node_03_editor import MemeGenEditor
from agents.meme_gen.state import MemeGenState, Research, Validation
from integration.configuration_module_factory import ConfigurationModuleFactory


class TestMemegenEditor:

    @pytest.fixture
    def node(self) -> MemeGenEditor:
        editor = ConfigurationModuleFactory.build(MemeGenEditor)
        editor.initialize()
        return editor

    @pytest.mark.asyncio
    async def test_run(self, node: MemeGenEditor):
        # Arrange
        state = MemeGenState()
        state.research = self._get_research()
        state.validation = self._get_validation()

        # Act
        final_state = await node.run(state)

        # Assert
        assert final_state.editor
        assert final_state.editor.meme_type
        assert final_state.editor.prompt

    @staticmethod
    def _get_research():
        return Research(**{
            "tool_call_status": True,
            "tool_call_reason": "Successfully retrieved funny facts related to the topics 'birthday party' and 'mountain hike'.",
            "combined_joke": "Why did the birthday cake go on a mountain hike? Because it wanted to blow out its candles at the peak and send its wishes to the gods—just like the Greeks! But it got lost and ended up sending a smoke signal to the parking lot instead!",
            "primary_topic": "birthday party",
            "primary_topic_reason": "Birthday parties are universally relatable and have a lot of humorous elements, such as cake, candles, and party mishaps.",
            "primary_topic_facts": [
                "Blowing out candles on a cake started with the Greeks, who believed that the smoke would carry their wishes to the gods.",
                "The tradition of birthday parties became popular in the 20th century, especially for children.",
                "The largest birthday cake ever made weighed over 128,000 pounds!"
            ],
            "secondary_topic": "mountain hike",
            "secondary_topic_reason": "Hiking is a popular outdoor activity that can lead to funny situations, especially when combined with the concept of a birthday party.",
            "secondary_topic_facts": [
                "The Appalachian Trail gets about 3 million hikers each year, with over 3,000 attempting to hike the entire trail.",
                "Hiking can improve mental health and overall well-being, making it a great way to celebrate life!",
                "Many hikers have funny stories about getting lost or encountering wildlife on the trails."
            ],
            "full_topics_list": [
                "afghanistan war",
                "covid 19",
                "birthday party",
                "mountain hike"
            ]
        })

    @staticmethod
    def _get_validation():
        return Validation(**{
            "iterations": 1,
            "primary_topic": "birthday party",
            "primary_topic_status": True,
            "primary_topic_reason": "The topic of 'birthday party' is universally relatable and humorous, involving elements like cake, candles, and party mishaps. It does not relate to any sensitive subjects such as politics, war, racism, or health issues. The search results confirmed that humor related to birthday parties does not raise legal or ethical concerns.",
            "secondary_topic": "mountain hike",
            "secondary_topic_status": True,
            "secondary_topic_reason": "The topic of 'mountain hike' is also light-hearted and does not involve sensitive subjects. Hiking is a popular outdoor activity that can lead to funny situations, and the search results indicated that humor related to hiking is generally acceptable without legal or ethical issues."
        })

