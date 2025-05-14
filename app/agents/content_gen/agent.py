import asyncio

from agents.content_gen.core import ContentGenCore
from configurations.configs import Configs
from crosscutting.logging.app_logger import AppLogger


class ContentGenAgent:
    def __init__(
            self,
            logger: AppLogger,
            configs: Configs,
            agent: ContentGenCore):

        self.logger = logger
        self.configs = configs
        self.agent = agent

    async def run_task(self, input):
        try:
            await self.agent.crew().kickoff_async(inputs=input)
        except asyncio.CancelledError:
            self.logger.warn("Agent running task cancelled.")

    async def run(self, input: dict) -> None:
        self.logger.highlight("Executing agent ...")

        await self.run_task(input)

        self.logger.highlight("Agent executed.")