from agents.meme_gen.state import MemeGenState
from crosscutting.logging.app_logger import AppLogger


class MemeGenEditor:

    NODE_NAME = "Editor"

    PROMPTS_FILE = "../prompts.yml"

    def __init__(self,
                 logger: AppLogger):

        self.logger = logger

    @AppLogger.timeit()
    async def run(self, state: MemeGenState):
        self.logger.highlight_2(f"Starting {self.NODE_NAME} ...")
        self.logger.info(f"Completed.")
        return state

    def flow_condition(self, state: MemeGenState) -> str:
        return "publisher"