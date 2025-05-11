import asyncio

from agent_langgraph.graph import ResearchAgentGraph
from crosscutting.app_logger import AppLogger
from crosscutting.graceful_shutdown import GracefulShutdown


class ResearchAgent:

    def __init__(self,
                 logger: AppLogger,
                 shutdown: GracefulShutdown,
                 builder: ResearchAgentGraph):

        self.logger = logger
        self.shutdown = shutdown
        self.builder = builder

    async def run_task(self, graph, input):
        try:
            async for step in graph.astream(input):
                self.logger.info(f"[{list(step.keys())[0]}] Step executed.")
            return await graph.ainvoke(input)
        except asyncio.CancelledError:
            self.logger.warn("Agent running task cancelled.")
            return None

    async def run(self, input: dict) -> None:
        self.logger.highlight("Executing agent ...")

        self.shutdown.reset()
        graph = self.builder.build()
        agent_task = asyncio.create_task(self.run_task(graph, input))
        shutdown_task = asyncio.create_task(self.shutdown.wait())

        done, pending = await asyncio.wait(
            [agent_task, shutdown_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        if self.shutdown.cancel_event.is_set():
            self.logger.warn("Terminating agent ...")
            agent_task.cancel()
            try:
                await agent_task
                self.logger.warn("Agent terminated.")
            except asyncio.CancelledError:
                self.logger.warn("Agent terminated.")
        elif agent_task in done:
            self.logger.highlight("Agent executed.")
            self.shutdown.finish()
            return agent_task.result()

        self.shutdown.finish()
        return None

    async def request_shutdown(self):
        await self.shutdown.request()
