from agents.meme_gen.state import MemeGenState
from crosscutting.logging.app_logger import AppLogger
from repositories.used_topics_repository import UsedTopicsRepository


class MemeGenInitializer:

    NODE_NAME = "Initializer"

    def __init__(self,
                 logger: AppLogger,
                 used_topics_repository: UsedTopicsRepository):

        self.logger = logger
        self.used_topics_repository = used_topics_repository

    async def run(self, state: MemeGenState):
        self.logger.highlight_2(f"Starting {self.NODE_NAME} ...")
        topics = await self.used_topics_repository.get_all_topic_names()
        state.prior_topics = set(topics)
        state.trend_research = None
        state.trend_research_validation = None
        return state