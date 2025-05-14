import asyncio
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, END

from agents.meme_gen.core import MemeGenCore
from agents.meme_gen.state import PortfolioState


class MemeGenGraph:

    def __init__(self, core: MemeGenCore):
        self.core = core

    def build(self):
        self.core.initialize()

        builder = StateGraph(PortfolioState)
        builder.add_node("MusicAgent", RunnableLambda(lambda state: asyncio.run(self.core.music_agent(state))))
        builder.add_node("TechAgent", RunnableLambda(lambda state: asyncio.run(self.core.tech_agent(state))))
        builder.add_node("NarrativeAgent", RunnableLambda(lambda state: asyncio.run(self.core.narrative_agent(state))))
        builder.add_node("EditorAgent", RunnableLambda(lambda state: asyncio.run(self.core.editor_agent(state))))

        builder.set_entry_point("MusicAgent")
        builder.add_edge("MusicAgent", "TechAgent")
        builder.add_edge("TechAgent", "NarrativeAgent")
        builder.add_edge("NarrativeAgent", "EditorAgent")
        builder.add_edge("EditorAgent", END)

        return builder.compile()