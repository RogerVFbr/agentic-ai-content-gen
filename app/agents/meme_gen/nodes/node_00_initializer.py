from agents.meme_gen.state import MemeGenState
from crosscutting.logging.app_logger import AppLogger


class MemeGenInitializer:

    NODE_NAME = "Initializer"

    def __init__(self,
                 logger: AppLogger):

        self.logger = logger

    async def run(self, state: MemeGenState):
        self.logger.highlight_2(f"Starting {self.NODE_NAME} ...")
        state.trend_research = None
        state.trend_research_validation = None
        return state