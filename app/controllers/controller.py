from agents.meme_gen.agent import MemeGenAgent
from crosscutting.logging.app_logger import AppLogger


class MemeGenController:

    def __init__(self,
                 logger: AppLogger,
                 agent: MemeGenAgent):

        self._logger = logger
        self._agent = agent

    @AppLogger.timeit()
    async def initialize(self) -> None:
        try:
            self._logger.info("Initializing agent ...")
            await self._agent.initialize()
        except Exception as e:
            self._logger.critical(f"An error occurred while initializing the agent: {e}.", exception=e)
            raise e

    @AppLogger.timeit()
    async def run(self, input: dict) -> None:
        try:
            self._logger.highlight_1("Running agent ...")
            _ = await self._agent.run(input)
            self._logger.highlight_1("Agent finished.")
        except Exception as e:
            self._logger.critical(f"An error occurred while running the agent: {e}.", exception=e)
            raise e

    @AppLogger.timeit()
    async def terminate(self) -> None:
        try:
            self._logger.highlight_1("Shutting down ...")
            await self._agent.terminate()
            self._logger.highlight_1("Shutdown completed.")
        except Exception as e:
            self._logger.critical(f"An error occurred while shutting down the application: {e}.", exception=e)
            raise e
