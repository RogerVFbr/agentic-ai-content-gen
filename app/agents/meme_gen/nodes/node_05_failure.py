from agents.meme_gen.state import MemeGenState
from crosscutting.logging.app_logger import AppLogger


class MemeGenFailure:

    NODE_NAME = "Failure"

    def __init__(self,
                 logger: AppLogger):

        self._logger = logger

    async def run(self, state: MemeGenState):
        self._logger.error("Agent run failed.")
        return state