import os
from langchain_core.prompts import PromptTemplate
from langgraph.prebuilt import create_react_agent

from agents.meme_gen.nodes.node_base import MemeGenBase
from agents.meme_gen.state import MemeGenState, Research
from crosscutting.logging.app_logger import AppLogger
from repositories.web_search_repository import WebSearchRepository
from repositories.web_trends_repository import WebTrendsRepository


class MemeGenTrendResearcher(MemeGenBase):

    NODE_NAME = "Researcher"

    PROMPTS_FILE = "../prompts.yml"

    def __init__(self,
                 logger: AppLogger,
                 web_search_repository: WebSearchRepository,
                 web_trends_repository: WebTrendsRepository):

        super().__init__(logger)

        self._logger = logger
        self._web_trends_repository = web_trends_repository
        self._web_search_repository = web_search_repository

        self._user_prompt = None
        self._agent = None

        self._prompts_file = os.path.join(os.path.dirname(__file__), self.PROMPTS_FILE)

    def initialize(self):
        prompts = self.load_prompts(self._prompts_file, "researcher")

        self._user_prompt = PromptTemplate(
            input_variables=["time_now", "current_trends"],
            template=prompts["user"]
        )

        self._agent = create_react_agent(
            model=self.get_llm(),
            prompt=prompts["system"],
            response_format=Research,
            tools=[self._search_web],
            debug=False
        )

    @AppLogger.timeit()
    async def run(self, state: MemeGenState):
        self._logger.highlight_2(f"Starting {self.NODE_NAME} ...")
        self._web_search_repository.reset_quota(self.NODE_NAME)
        prompt = await self._build_prompt(state)

        response = None
        async for step in self._agent.astream(prompt):
            await self.log_progress(step)
            response = step

        state = self._update_state(state, response)
        self._logger.info(f"Completed. Topics: '{state.research.primary_topic}' and '{state.research.secondary_topic}'.", data=state.research.__dict__)
        return state

    async def _build_prompt(self, state: MemeGenState):
        current_trends = await self._web_trends_repository.get_trending_now("US", sorted(list(state.prior_topics)), 10)

        prompt = self._user_prompt.format(
            time_now=self.time_now(),
            current_trends=current_trends
        )

        return self.get_user_message(prompt)

    async def _search_web(self, query: str):
        """Executes searches on the web"""
        return await self._web_search_repository.search(self.NODE_NAME, query)

    def _update_state(self, state: MemeGenState, response):
        state.research = self.get_structured_response(response)
        state.prior_topics.add(state.research.primary_topic)
        state.prior_topics.add(state.research.secondary_topic)
        return state

    def flow_condition(self, state: MemeGenState) -> str:
        if state.research.tool_call_status:
            return "validator"

        self._logger.warn("Research aborted due to tool call failure.")
        return "end"