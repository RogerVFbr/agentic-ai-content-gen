import asyncio
from langchain_core.messages import AIMessage

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
            graph = self.graph.build()
            async for step in graph.astream(input):
                self.logger.info(f"[{list(step.keys())[0]}] Step executed.")
        except asyncio.CancelledError:
            self.logger.warn("Agent execution cancelled.")