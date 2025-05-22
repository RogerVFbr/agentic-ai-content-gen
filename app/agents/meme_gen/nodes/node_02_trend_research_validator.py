import copy
import json
import os
from langchain_core.prompts import PromptTemplate
from langgraph.prebuilt import create_react_agent

from agents.meme_gen.nodes.node_00_base import MemeGenBase
from agents.meme_gen.state import MemeGenState, TrendResearchValidationStatus
from crosscutting.logging.app_logger import AppLogger
from crosscutting.memoize_method import memoize_method
from infrastructure.serper_dev_client import SerperDevClient
from infrastructure.tavily_client import TavilyClient


class MemeGenTrendValidator(MemeGenBase):

    NODE_NAME = "TrendResearchValidator"

    PROMPTS_FILE = "../prompts.yml"

    def __init__(self,
                 logger: AppLogger,
                 serper_dev_client: SerperDevClient,
                 tavily_client: TavilyClient):

        super().__init__(logger)
        self.logger = logger
        self.serper_dev_client = serper_dev_client
        self.tavily_client = tavily_client

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
                self.tavily_client.search,
                # self.serper_dev_client.search,
                # self.thoughts
            ],
            debug=False,
        )

    async def run(self, state: MemeGenState):
        self.logger.highlight_2(f"Starting {self.NODE_NAME} ...")

        research = state.trend_research.__dict__.copy()
        del research['search_tool_call_status']
        del research['search_tool_call_reason']
        del research['full_topics_list']
        research = json.dumps(research)

        response = await self.agent.ainvoke(
            self.get_user_message(
                self.user_prompt.template.format(time_now=self.time_now(), research=research))
        )

        state = self._update_state(state, response)
        self.logger.info("Completed.", data=state.trend_research_validation.__dict__)
        return state

    @staticmethod
    def _update_state(state: MemeGenState, response):
        orig_validation = copy.deepcopy(state.trend_research_validation) if state.trend_research_validation else None
        state.trend_research_validation = response["structured_response"]

        if orig_validation:
            if orig_validation.primary_topic_status:
                state.trend_research_validation.primary_topic = orig_validation.primary_topic
                state.trend_research_validation.primary_topic_status = orig_validation.primary_topic_status
                state.trend_research_validation.primary_topic_reason = orig_validation.primary_topic_reason
            if orig_validation.secondary_topic_status:
                state.trend_research_validation.secondary_topic = orig_validation.secondary_topic
                state.trend_research_validation.secondary_topic_status = orig_validation.secondary_topic_status
                state.trend_research_validation.secondary_topic_reason = orig_validation.secondary_topic_reason

        state.trend_research_validation.iterations = orig_validation.iterations + 1 if orig_validation else 1

        return state

    def flow_condition(self, state: MemeGenState) -> str:
        primary_status = state.trend_research_validation.primary_topic_status
        secondary_status = state.trend_research_validation.secondary_topic_status

        if primary_status and secondary_status:
            return "end"

        if state.trend_research_validation.iterations >= 4:
            self.logger.warn("Research and compliance teams could not get to an agreement.")
            return "end"

        return "researcher"
