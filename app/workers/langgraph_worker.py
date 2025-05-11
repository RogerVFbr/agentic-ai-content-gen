from controllers.langgraph_controller import LangGraphController
from crosscutting.background_service import BackgroundService


class LangGraphWorker(BackgroundService):

    def __init__(self, controller: LangGraphController):
        super().__init__()
        self.controller = controller

    async def start(self, input=None):
        await self.controller.run(input)

    async def stop(self):
        await self.controller.terminate()