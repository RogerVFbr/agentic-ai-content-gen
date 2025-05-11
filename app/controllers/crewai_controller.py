from configurations.configs import Configs
from crosscutting.app_logger import AppLogger
from agent_crewai.crew import ContentGen


class CrewAiController:
    IS_TERMINATION_INFLIGHT = False

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
            self.logger.highlight("Executing agent_crewai ...")
            await self.agent.crew().kickoff_async(inputs=input)
            self.logger.highlight("Agent executed.")
        except Exception as e:
            raise Exception(f"An error occurred while running the crew: {e}")

    async def terminate(self, signum, _) -> None:
        self.logger.highlight(f"Termination requested (Signum: {signum}). Shutting down ...")
