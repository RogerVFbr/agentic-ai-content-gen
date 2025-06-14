from agents.meme_gen.state import MemeGenState
from crosscutting.logging.app_logger import AppLogger
from repositories.used_topics_repository import UsedTopicsRepository
from repositories.web_search_repository import WebSearchRepository


class MemeGenTerminate:

    NODE_NAME = "Terminate"

    def __init__(self,
                 logger: AppLogger,
                 used_topics_repository: UsedTopicsRepository,
                 web_search_repository: WebSearchRepository):

        self._logger = logger
        self._used_topics_repository = used_topics_repository
        self._web_search_repository = web_search_repository

    async def run(self, state: MemeGenState):
        self._logger.info("Terminating agent.")
        await self._used_topics_repository.add_topics_batch(state.prior_topics)
        return state

    async def terminate(self):
        await self._used_topics_repository.flush()
        self._web_search_repository.flush()
