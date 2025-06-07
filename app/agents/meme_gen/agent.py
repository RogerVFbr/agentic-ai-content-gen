import asyncio

from agents.meme_gen.graph import MemeGenGraphBuilder
from crosscutting.logging.app_logger import AppLogger


class MemeGenAgent:

    def __init__(self,
                 logger: AppLogger,
                 builder: MemeGenGraphBuilder):

        self.logger = logger
        self.builder = builder
        self.graph = None

    async def initialize(self):
        await self.builder.initialize()
        self.graph = await self.builder.build()

    async def run(self, input: dict) -> None:
        try:
            config = {"configurable": {"thread_id": "3"}}
            async for step in self.graph.astream({}, config=config):
                self.logger.info(f"Graph: '{list(step.keys())[0]}' node executed.")
        except asyncio.CancelledError:
            self.logger.warn("Agent execution cancelled.")

    async def terminate(self):
        await self.builder.terminate()
