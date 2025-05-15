from langgraph.graph import StateGraph, END

from agents.meme_gen.agent_01_trend_researcher import MemeGenTrendResearcher
from agents.meme_gen.agent_02_trend_research_validator import MemeGenTrendValidator
from agents.meme_gen.state import MemeGenState


class MemeGenGraph:

    def __init__(self,
                 trend_researcher: MemeGenTrendResearcher,
                 trend_research_validator: MemeGenTrendValidator):

        self.trend_researcher = trend_researcher
        self.trend_research_validator = trend_research_validator

    def build(self):
        self.trend_researcher.initialize()
        self.trend_research_validator.initialize()

        builder = StateGraph(MemeGenState)

        builder.add_node("TrendResearcher", self.trend_researcher.run)
        builder.add_node("TrendResearchValidator", self.trend_research_validator.run)

        builder.set_entry_point("TrendResearcher")

        builder.add_edge("TrendResearcher", "TrendResearchValidator")
        builder.add_edge("TrendResearchValidator", END)

        return builder.compile()