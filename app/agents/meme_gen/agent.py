import asyncio

from agents.meme_gen.graph import MemeGenGraph
from crosscutting.logging.app_logger import AppLogger


class MemeGenAgent:

    def __init__(self,
                 logger: AppLogger,
                 graph: MemeGenGraph):

        self.logger = logger
        self.graph = graph

    async def run(self, input: dict) -> None:
        try:
            agent_graph = await self.graph.build()
            config = {"configurable": {"thread_id": "3"}}
            async for step in agent_graph.astream({}, config=config):
                self.logger.info(f"Graph: '{list(step.keys())[0]}' node executed.")
        except asyncio.CancelledError:
            self.logger.warn("Agent execution cancelled.")

    async def terminate(self):
        await self.graph.terminate()
