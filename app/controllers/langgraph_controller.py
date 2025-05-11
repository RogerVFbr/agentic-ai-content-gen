import asyncio

from agent_langgraph.agent import ResearchAgent
from configurations.configs import Configs
from crosscutting.app_logger import AppLogger


class LangGraphController:

    IS_TERMINATION_INFLIGHT = False

    def __init__(
            self,
            logger: AppLogger,
            configs: Configs,
            agent: ResearchAgent):

        self.logger = logger
        self.configs = configs
        self.agent = agent

    @AppLogger.timeit()
    async def run(self, input: dict) -> None:
        try:
            _ = await self.agent.run(input)

            while self.IS_TERMINATION_INFLIGHT:
                await asyncio.sleep(0.3)

        except Exception as e:
            raise Exception(f"An error occurred while running the agent: {e}")

    @AppLogger.timeit()
    async def terminate(self, signum, _) -> None:
        self.IS_TERMINATION_INFLIGHT = True
        self.logger.highlight(f"Termination requested (Signum: {signum}). Shutting down ...")

        await self.agent.request_shutdown()

        self.logger.highlight("Shutdown completed.")
        self.IS_TERMINATION_INFLIGHT = False