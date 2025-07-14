from configurations.configs import Configs
from controllers.controller import MemeGenController
from crosscutting.background_service.one_shot_background_service import OneShotBackgroundService, CancellationToken
from crosscutting.logging.app_logger import AppLogger


class MemeGenWorker(OneShotBackgroundService):

    def __init__(self,
                 logger: AppLogger,
                 configs: Configs,
                 controller: MemeGenController):

        super().__init__(raise_on_failure=configs.flags.raise_exception_on_critical_failure)
        self.controller = controller
        self.logger = logger

    async def on_initialize(self):
        await self.controller.initialize()

    async def start(self, cancellation_token: CancellationToken, input=None):
        await self.controller.run(input)

    async def stop(self, cancellation_token: CancellationToken, input=None):
        await self.controller.terminate()

    async def on_terminate(self):
        self.logger.warn("Termination requested ...")