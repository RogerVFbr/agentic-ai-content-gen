from agents.content_gen.agent import ContentGenAgent
from crosscutting.logging.app_logger import AppLogger


class ContentGenController:
    def __init__(
            self,
            logger: AppLogger,
            agent: ContentGenAgent):

        self.logger = logger
        self.agent = agent

    @AppLogger.timeit()
    async def run(self, input: dict) -> None:
        try:
            await self.agent.run(input)
        except Exception as e:
            raise Exception(f"An error occurred while running the crew: {e}")

    @AppLogger.timeit()
    async def terminate(self) -> None:
        self.logger.highlight("Shutting down ...")
        self.logger.highlight("Shutdown completed.")
