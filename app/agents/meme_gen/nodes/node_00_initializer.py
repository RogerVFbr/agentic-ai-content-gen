from agents.meme_gen.state import MemeGenState
from crosscutting.logging.app_logger import AppLogger
from repositories.used_topics_repository import UsedTopicsRepository


class MemeGenInitializer:

    NODE_NAME = "Initializer"

    def __init__(self,
                 logger: AppLogger,
                 used_topics_repository: UsedTopicsRepository):

        self._logger = logger
        self._used_topics_repository = used_topics_repository

    async def initialize(self):
        await self._used_topics_repository.load()

    async def run(self, state: MemeGenState):
        self._logger.highlight_2(f"Starting {self.NODE_NAME} ...")
        topics = await self._used_topics_repository.get_all_topic_names()
        state.prior_topics = set(topics)
        state.research = None
        state.validation = None
        return state