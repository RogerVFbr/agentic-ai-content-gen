from controllers.crewai_controller import CrewAiController
from crosscutting.background_service import BackgroundService


class CrewAiWorker(BackgroundService):

    def __init__(self, controller: CrewAiController):
        super().__init__()
        self.controller = controller

    async def start(self, input=None):
        await self.controller.run(input)

    async def stop(self):
        await self.controller.terminate()