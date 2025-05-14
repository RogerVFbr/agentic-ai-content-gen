import asyncio
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, END

from agents.meme_gen.agent_trend_researcher import MemeGenTrendResearcher
from agents.meme_gen.state import MemeGenState


class MemeGenGraph:

    def __init__(self,
                 trend_researcher: MemeGenTrendResearcher):

        self.trend_researcher = trend_researcher

    def build(self):
        self.trend_researcher.initialize()

        builder = StateGraph(MemeGenState)

        builder.add_node("TrendResearcher", RunnableLambda(lambda state: asyncio.run(self.trend_researcher.run(state))))

        builder.set_entry_point("TrendResearcher")
        builder.add_edge("TrendResearcher", END)

        return builder.compile()