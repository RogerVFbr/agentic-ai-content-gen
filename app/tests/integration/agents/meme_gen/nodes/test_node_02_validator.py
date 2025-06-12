import pytest

from agents.meme_gen.nodes.node_02_validator import MemeGenTrendValidator
from agents.meme_gen.state import MemeGenState, TrendResearch
from integration.configuration_module_factory import ConfigurationModuleFactory


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
        state.trend_research = self._get_valid_trends()
        state.trend_research_validation = None

        # Act
        final_state = await node.run(state)

        # Assert
        assert final_state.trend_research_validation is not None
        assert final_state.trend_research_validation.primary_topic_status
        assert final_state.trend_research_validation.primary_topic == "birthday party"
        assert final_state.trend_research_validation.primary_topic_reason
        assert final_state.trend_research_validation.secondary_topic_status
        assert final_state.trend_research_validation.secondary_topic == "mountain hike"
        assert final_state.trend_research_validation.secondary_topic_reason

    @pytest.mark.asyncio
    async def test_run_invalid_trends(self, node: MemeGenTrendValidator):
        # Arrange
        state = MemeGenState()
        state.trend_research = self._get_invalid_trends()
        state.trend_research_validation = None

        # Act
        final_state = await node.run(state)

        # Assert
        assert final_state.trend_research_validation is not None
        assert not final_state.trend_research_validation.primary_topic_status
        assert final_state.trend_research_validation.primary_topic == "afghanistan war"
        assert final_state.trend_research_validation.primary_topic_reason
        assert not final_state.trend_research_validation.secondary_topic_status
        assert final_state.trend_research_validation.secondary_topic == "covid 19"
        assert final_state.trend_research_validation.secondary_topic_reason

    @staticmethod
    def _get_valid_trends():
        return TrendResearch(**{
            "search_tool_call_status": True,
            "search_tool_call_reason": "Successfully retrieved funny facts related to the topics 'birthday party' and 'mountain hike'.",
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
    def _get_invalid_trends():
        return TrendResearch(**{
            "search_tool_call_status": True,
            "search_tool_call_reason": "Successfully retrieved funny facts related to the topics.",
            "combined_joke": "Why did covid erupt in the afghanistan war? Because it got a cold.",
            "primary_topic": "afghanistan war",
            "primary_topic_reason": "Afghanistan war is a topic suitable for a meme.",
            "primary_topic_facts": [
                "The U.S.-led war in Afghanistan (2001–2021) was America’s longest military conflict.",
                "The Soviet Union invaded Afghanistan in 1979, triggering a decade-long war against U.S.-backed Afghan resistance fighters known as the mujahideen.",
                "After being ousted in 2001, the Taliban gradually regained strength and returned to power in 2021 following the withdrawal of U.S. and NATO forces."
            ],
            "secondary_topic": "covid 19",
            "secondary_topic_reason": "Covid 19 war is a topic suitable for a meme.",
            "secondary_topic_facts": [
                "COVID-19 is caused by the SARS-CoV-2 virus, which is a type of coronavirus.",
                "It primarily spreads through respiratory droplets when an infected person coughs, sneezes, or talks.",
                "The World Health Organization declared COVID-19 a global pandemic on March 11, 2020, leading to widespread health, social, and economic effects worldwide."
            ],
            "full_topics_list": [
                "afghanistan war",
                "covid 19",
                "birthday party",
                "mountain hike"
            ]
        })