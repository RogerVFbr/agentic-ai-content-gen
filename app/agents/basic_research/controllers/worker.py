from agents.basic_research.controllers.controller import BasicResearchController
from crosscutting.logging.app_logger import AppLogger
from crosscutting.background_service import BackgroundService, CancellationToken


class BasicResearchWorker(BackgroundService):

    def __init__(self,
                 logger: AppLogger,
                 controller: BasicResearchController):

        super().__init__()
        self.controller = controller
        self.logger = logger

    async def start(self, cancellation_token: CancellationToken, input=None):
        await self.controller.run(input)

    async def stop(self):
        await self.controller.terminate()

    async def on_terminate(self):
        self.logger.warn("Termination requested ...")