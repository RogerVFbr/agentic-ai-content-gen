from agent_langgraph.agent import ResearchAgent
from configurations.configs import Configs
from crosscutting.app_lifecycle import AppLifecycle
from crosscutting.app_logger import AppLogger


class LangGraphController:

    def __init__(
            self,
            logger: AppLogger,
            configs: Configs,
            agent: ResearchAgent):

        self.logger = logger
        self.configs = configs
        self.agent = agent

    @AppLifecycle.main()
    @AppLogger.timeit()
    async def run(self, input: dict) -> None:
        try:
            _ = await self.agent.run(input)
        except Exception as e:
            self.logger.error(f"An error occurred while running the agent: {e}.", exception=e)
            # raise

    @AppLifecycle.terminate()
    @AppLogger.timeit()
    async def terminate(self, signum = None, _ = None) -> None:
        if signum:
            self.logger.warn(f"Termination requested (Signum: {signum}).")
        self.logger.highlight("Shutting down ...")

        await self.agent.terminate()

        self.logger.highlight("Shutdown completed.")