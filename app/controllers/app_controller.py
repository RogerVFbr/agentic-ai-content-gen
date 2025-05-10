from configurations.configs import Configs
from crosscutting.app_logger import AppLogger
from agent.crew import ContentGen


class AppController:
    def __init__(
            self,
            logger: AppLogger,
            configs: Configs,
            agent: ContentGen):

        self.logger = logger
        self.configs = configs
        self.agent = agent

    @AppLogger.timeit()
    async def run(self, input: dict) -> None:
        try:
            self.logger.highlight("Executing agent ...")
            await self.agent.crew().kickoff_async(inputs=input)
            self.logger.highlight("Agent executed.")
        except Exception as e:
            raise Exception(f"An error occurred while running the crew: {e}")

    def terminate(self, signum, frame) -> None:
        self.logger.highlight("Termination requested. Shutting down ...")
