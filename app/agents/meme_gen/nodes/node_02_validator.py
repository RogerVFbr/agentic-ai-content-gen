import copy
import json
import os
from langchain_core.prompts import PromptTemplate
from langgraph.prebuilt import create_react_agent

from agents.meme_gen.nodes.node_base import MemeGenBase
from agents.meme_gen.state import MemeGenState, TrendResearchValidationStatus
from crosscutting.logging.app_logger import AppLogger
from crosscutting.memoize_method import memoize_method
from repositories.web_search_repository import WebSearchRepository


class MemeGenTrendValidator(MemeGenBase):

    NODE_NAME = "Validator"

    PROMPTS_FILE = "../prompts.yml"

    def __init__(self,
                 logger: AppLogger,
                 web_search_repository: WebSearchRepository):

        super().__init__(logger)

        self.logger = logger
        self.web_search_repository = web_search_repository

        self.system_prompt = None
        self.user_prompt = None
        self.agent = None

        self.prompts_file = os.path.join(os.path.dirname(__file__), self.PROMPTS_FILE)

    @memoize_method()
    def initialize(self):
        prompts = self.load_prompts(self.prompts_file)["trend_research_validator"]

        self.system_prompt = prompts["system"]

        self.user_prompt = PromptTemplate(
            input_variables=["time_now", "research"],
            template=prompts["user"]
        )

        self.agent = create_react_agent(
            model=self.get_llm(),
            prompt=self.system_prompt,
            response_format=TrendResearchValidationStatus,
            tools=[
                self._search_web
            ],
            debug=False,
        )

    @AppLogger.timeit()
    async def run(self, state: MemeGenState):
        self.logger.highlight_2(f"Starting {self.NODE_NAME} ...")

        self.web_search_repository.reset_quota(self.NODE_NAME)

        research = state.trend_research.__dict__.copy()
        del research['search_tool_call_status']
        del research['search_tool_call_reason']
        del research['full_topics_list']
        research = json.dumps(research)

        user_message = self.get_user_message(self.user_prompt.template.format(
            time_now=self.time_now(),
            research=research))

        final_response = None
        async for response in self.agent.astream(user_message):
            await self.log_progress(response)
            final_response = response

        state = self._update_state(state, final_response)
        self.logger.info("Completed.", data=state.trend_research_validation.__dict__)
        return state

    async def _search_web(self, query: str):
        """Executes searches on the web"""
        return await self.web_search_repository.search(self.NODE_NAME, query)

    @staticmethod
    def _update_state(state: MemeGenState, response):
        orig_validation = copy.deepcopy(state.trend_research_validation) if state.trend_research_validation else None
        state.trend_research_validation = response["structured_response"]

        if state.trend_research_validation.primary_topic_status and not state.trend_research_validation.secondary_topic_status:
            state.prior_topics.remove(state.trend_research.primary_topic)
        elif not state.trend_research_validation.primary_topic_status and state.trend_research_validation.secondary_topic_status:
            state.prior_topics.remove(state.trend_research.secondary_topic)

        state.trend_research_validation.iterations = orig_validation.iterations + 1 if orig_validation else 1

        return state

    def flow_condition(self, state: MemeGenState) -> str:
        primary_status = state.trend_research_validation.primary_topic_status
        secondary_status = state.trend_research_validation.secondary_topic_status

        if primary_status and secondary_status:
            return "editor"

        if state.trend_research_validation.iterations >= 4:
            self.logger.warn("Research and compliance teams could not get to an agreement.")
            return "end"

        return "researcher"
