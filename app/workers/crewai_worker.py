from controllers.crewai_controller import CrewAiController
from crosscutting.app_logger import AppLogger
from crosscutting.background_service import BackgroundService
from crosscutting.cancellation_token import CancellationToken


class CrewAiWorker(BackgroundService):

    def __init__(self,
                 logger: AppLogger,
                 controller: CrewAiController):

        super().__init__()
        self.controller = controller
        self.logger = logger

    async def start(self, cancellation_token: CancellationToken, input=None):
        await self.controller.run(input)

    async def stop(self):
        await self.controller.terminate()

    async def on_terminate(self):
        self.logger.warn("Termination requested ...")