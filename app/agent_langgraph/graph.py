import asyncio
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda

from agent_langgraph.elements import ResearchAgentElements
from agent_langgraph.state import PortfolioState


class ResearchAgentGraph:

    def __init__(self, elements: ResearchAgentElements):
        self.elements = elements

    def build(self):
        self.elements.initialize()

        builder = StateGraph(PortfolioState)
        builder.add_node("MusicAgent", RunnableLambda(lambda state: asyncio.run(self.elements.music_agent(state))))
        builder.add_node("TechAgent", RunnableLambda(lambda state: asyncio.run(self.elements.tech_agent(state))))
        builder.add_node("NarrativeAgent", RunnableLambda(lambda state: asyncio.run(self.elements.narrative_agent(state))))
        builder.add_node("EditorAgent", RunnableLambda(lambda state: asyncio.run(self.elements.editor_agent(state))))

        builder.set_entry_point("MusicAgent")
        builder.add_edge("MusicAgent", "TechAgent")
        builder.add_edge("TechAgent", "NarrativeAgent")
        builder.add_edge("NarrativeAgent", "EditorAgent")
        builder.add_edge("EditorAgent", END)

        return builder.compile()