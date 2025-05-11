import asyncio
import time
from configurations.configs import Configs
from crosscutting.app_logger import AppLogger
from agent.crew import ContentGen
from crosscutting.graceful_shutdown import GracefulShutdown
from main_langgraph import LangGraphBuilder, LangGraphRunner


class AppController:

    IS_TERMINATION_INFLIGHT = False

    def __init__(
            self,
            logger: AppLogger,
            configs: Configs,
            agent: ContentGen,
            agent_shutdown: GracefulShutdown):

        self.logger = logger
        self.configs = configs
        self.agent = agent
        self.agent_shutdown = agent_shutdown

    # @AppLogger.timeit()
    # async def run(self, input: dict) -> None:
    #     try:
    #         self.logger.highlight("Executing agent ...")
    #         await self.agent.crew().kickoff_async(inputs=input)
    #         self.logger.highlight("Agent executed.")
    #     except Exception as e:
    #         raise Exception(f"An error occurred while running the crew: {e}")

    @AppLogger.timeit()
    async def run(self, input: dict) -> None:
        self.agent_shutdown.reset()

        input_data = {
            "raw_input": (
                "Roger Freret is a Grammy-nominated audio engineer and senior software architect "
                "at a major Brazilian bank. He has worked with Antonio Adolfo, Leo Gandelman, Blitz, "
                "and Flavio Venturini. He's also a certified AWS expert and speaker on DevOps and cloud architecture."
            )
        }

        graph = LangGraphBuilder().build()
        runner = LangGraphRunner(graph, input_data)

        task = asyncio.create_task(runner.run())
        shutdown_task = asyncio.create_task(self.agent_shutdown.wait())  # Wrap shutdown.wait in a task

        done, pending = await asyncio.wait(
            [task, shutdown_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        if self.agent_shutdown.cancel_event.is_set():
            self.logger.warn("Terminating agent execution due to shutdown request...")
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                self.logger.info("Agent execution successfully terminated by shutdown request.")
                self.agent_shutdown.is_running = False

        elif task in done:
            result = task.result()
            print("\n=== Final Portfolio Output ===\n")
            print(result["final_portfolio"])

        while self.IS_TERMINATION_INFLIGHT:
            self.logger.info("Waiting for termination request to be processed ...")
            await asyncio.sleep(1)

    async def terminate(self, signum, _) -> None:
        self.IS_TERMINATION_INFLIGHT = True
        self.logger.highlight(f"Termination requested ({signum.name}). Shutting down ...")
        await self.agent_shutdown.request()
        self.logger.highlight("Termination request finished.")
        self.IS_TERMINATION_INFLIGHT = False


