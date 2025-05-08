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

    def run(self):
        try:
            result = self.agent.crew().kickoff()
            print(result.raw)
        except Exception as e:
            raise Exception(f"An error occurred while running the crew: {e}")