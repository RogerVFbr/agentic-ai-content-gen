from agents.meme_gen.state import MemeGenState
from crosscutting.logging.app_logger import AppLogger
from repositories.used_topics_repository import UsedTopicsRepository


class MemeGenSuccess:

    NODE_NAME = "Success"

    def __init__(self,
                 logger: AppLogger,
                 used_topics_repository: UsedTopicsRepository):

        self.logger = logger
        self.used_topics_repository = used_topics_repository

    async def run(self, state: MemeGenState):
        self.logger.info("Agent completed successfully.")
        await self.used_topics_repository.add_topics_batch(state.prior_topics)
        return state