from agents.meme_gen.state import MemeGenState
from crosscutting.logging.app_logger import AppLogger


class MemeGenSuccess:

    NODE_NAME = "Success"

    def __init__(self,
                 logger: AppLogger):

        self._logger = logger

    async def run(self, state: MemeGenState):
        self._logger.info("Agent completed successfully.")
        return state