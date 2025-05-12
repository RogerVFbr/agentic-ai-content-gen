import asyncio

from agent_langgraph.graph import ResearchAgentGraph
from crosscutting.app_logger import AppLogger


class ResearchAgent:

    def __init__(self,
                 logger: AppLogger,
                 graph: ResearchAgentGraph):

        self.logger = logger
        self.graph = graph

    async def run(self, input: dict) -> None:
        try:
            graph = self.graph.build()
            async for step in graph.astream(input):
                self.logger.info(f"[{list(step.keys())[0]}] Step executed.")
            await graph.ainvoke(input)
        except asyncio.CancelledError:
            self.logger.warn("Agent execution cancelled.")