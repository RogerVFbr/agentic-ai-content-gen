import asyncio

from agent_langgraph.graph import ResearchAgentGraph
from crosscutting.app_logger import AppLogger


class ResearchAgent:

    def __init__(self,
                 logger: AppLogger,
                 graph: ResearchAgentGraph):

        self.logger = logger
        self.graph = graph

    async def run_task(self, graph, input):
        try:
            async for step in graph.astream(input):
                self.logger.info(f"[{list(step.keys())[0]}] Step executed.")
            return await graph.ainvoke(input)
        except asyncio.CancelledError:
            self.logger.warn("Agent running task cancelled.")
            return None

    async def run(self, input: dict) -> None:
        self.logger.highlight("Executing agent ...")

        graph = self.graph.build()
        await self.run_task(graph, input)

        self.logger.highlight("Agent executed.")