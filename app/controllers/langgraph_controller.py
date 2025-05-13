from agents.langgraph.agent import ResearchAgent
from crosscutting.logging.app_logger import AppLogger


class LangGraphController:

    def __init__(
            self,
            logger: AppLogger,
            agent: ResearchAgent):

        self.logger = logger
        self.agent = agent

    @AppLogger.timeit()
    async def run(self, input: dict) -> None:
        try:
            self.logger.highlight("Running agent ...")
            _ = await self.agent.run(input)
            self.logger.highlight("Agent finished.")
        except Exception as e:
            self.logger.critical(f"An error occurred while running the agent: {e}.", exception=e)

    @AppLogger.timeit()
    async def terminate(self) -> None:
        self.logger.highlight("Shutting down ...")
        self.logger.highlight("Shutdown completed.")