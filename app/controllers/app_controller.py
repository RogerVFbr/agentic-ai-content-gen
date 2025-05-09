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
    def run(self, input: dict) -> None:
        try:
            self.logger.highlight("Executing agent ...")
            result = self.agent.crew().kickoff(inputs=input)
            # self.logger.highlight(result.raw)
            self.logger.highlight("Agent execution finished.")

        except Exception as e:
            raise Exception(f"An error occurred while running the crew: {e}")