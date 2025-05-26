from agents.meme_gen.state import MemeGenState
from crosscutting.logging.app_logger import AppLogger


class MemeGenSuccess:

    NODE_NAME = "Success"

    def __init__(self,
                 logger: AppLogger):

        self.logger = logger

    async def run(self, state: MemeGenState):
        self.logger.info("Agent completed successfully.")
        return state