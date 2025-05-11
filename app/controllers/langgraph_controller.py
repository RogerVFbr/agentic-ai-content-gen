from agent_langgraph.agent import ResearchAgent
from crosscutting.app_logger import AppLogger


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
            _ = await self.agent.run(input)
        except Exception as e:
            self.logger.error(f"An error occurred while running the agent: {e}.", exception=e)
            # raise

    @AppLogger.timeit()
    async def terminate(self) -> None:
        self.logger.highlight("Shutting down ...")
        self.logger.highlight("Shutdown completed.")