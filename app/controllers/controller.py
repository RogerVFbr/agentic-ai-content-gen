from agents.meme_gen.agent import MemeGenAgent
from crosscutting.logging.app_logger import AppLogger


class MemeGenController:

    def __init__(self,
                 logger: AppLogger,
                 agent: MemeGenAgent):

        self.logger = logger
        self.agent = agent

    @AppLogger.timeit()
    async def initialize(self) -> None:
        try:
            self.logger.info("Initialization requested ...")
            await self.agent.initialize()
        except Exception as e:
            self.logger.critical(f"An error occurred while running the agent: {e}.", exception=e)
            raise e

    @AppLogger.timeit()
    async def run(self, input: dict) -> None:
        try:
            self.logger.highlight_1("Running agent ...")
            _ = await self.agent.run(input)
            self.logger.highlight_1("Agent finished.")
        except Exception as e:
            self.logger.critical(f"An error occurred while running the agent: {e}.", exception=e)
            raise e

    @AppLogger.timeit()
    async def terminate(self) -> None:
        try:
            self.logger.highlight_1("Shutting down ...")
            await self.agent.terminate()
            self.logger.highlight_1("Shutdown completed.")
        except Exception as e:
            self.logger.critical(f"Unable to gracefully shutdown the application: {e}.", exception=e)
            raise e
