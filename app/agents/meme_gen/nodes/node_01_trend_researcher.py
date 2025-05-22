import copy
import json
import os
from langchain_core.prompts import PromptTemplate
from langgraph.prebuilt import create_react_agent

from agents.meme_gen.nodes.node_00_base import MemeGenBase
from agents.meme_gen.state import MemeGenState, TrendResearch
from crosscutting.logging.app_logger import AppLogger
from crosscutting.memoize_method import memoize_method
from infrastructure.google_trends_client import GoogleTrendsClient
from infrastructure.serper_dev_client import SerperDevClient
from infrastructure.tavily_client import TavilyClient


class MemeGenTrendResearcher(MemeGenBase):

    NODE_NAME = "TrendResearcher"

    PROMPTS_FILE = "../prompts.yml"

    def __init__(self,
                 logger: AppLogger,
                 serper_dev_client: SerperDevClient,
                 tavily_client: TavilyClient,
                 google_trends_client: GoogleTrendsClient):

        super().__init__(logger)
        self.logger = logger
        self.google_trends_client = google_trends_client
        self.serper_dev_client = serper_dev_client
        self.tavily_client = tavily_client

        self.system_prompt = None
        self.user_main_prompt = None
        self.user_remake_prompt = None
        self.agent = None

        self.prompts_file = os.path.join(os.path.dirname(__file__), self.PROMPTS_FILE)

    @memoize_method()
    def initialize(self):
        prompts = self.load_prompts(self.prompts_file)["trend_researcher"]

        self.system_prompt = prompts["system"]

        self.user_main_prompt = PromptTemplate(
            input_variables=["time_now", "remake", "current_trends", "previous_assignment"],
            template=prompts["user"]["main"]
        )

        self.user_remake_prompt = PromptTemplate(
            input_variables=["to_replace", "to_keep"],
            template=prompts["user"]["remake"]
        )

        self.agent = create_react_agent(
            model=self.get_llm(),
            prompt=self.system_prompt,
            response_format=TrendResearch,
            tools=[
                self.tavily_client.search,
                # self.serper_dev_client.search,
                # self.thoughts
            ],
            debug=False,
        )

    async def run(self, state: MemeGenState):
        self.logger.highlight_2(f"Starting {self.NODE_NAME} ...")
        prompt = await self.build_prompt(state)
        response = await self.agent.ainvoke(self.get_user_message(prompt))
        state = self._update_state(state, response)
        self.logger.info("Completed.", data=state.trend_research.__dict__)
        return state

    async def build_prompt(self, state: MemeGenState):
        previous_assignment_str = "No previous assignments found."
        remake = "-"

        # self.logger.debug("Prior topics.", data=", ".join(sorted(list(state.prior_topics))) if len(state.prior_topics) > 0 else "No prior topics found.")

        current_trends = await self.google_trends_client.get_trending_now("US", sorted(list(state.prior_topics)))

        validation = state.trend_research_validation

        if validation:
            previous_assignment_str = json.dumps(state.trend_research.__dict__)
            if not validation.primary_topic_status and validation.secondary_topic_status:
                remake = self.user_remake_prompt.format(
                    to_replace="primary",
                    to_keep="secondary",
                )
            if validation.primary_topic_status and not validation.secondary_topic_status:
                remake = self.user_remake_prompt.format(
                    to_replace="secondary",
                    to_keep="primary",
                )

        prompt = self.user_main_prompt.format(
            time_now=self.time_now(),
            remake=remake,
            current_trends=current_trends,
            previous_assignment=previous_assignment_str
        )

        return prompt

    @staticmethod
    def _update_state(state: MemeGenState, response):
        orig_research = copy.deepcopy(state.trend_research) if state.trend_research else None
        state.trend_research = response["structured_response"]

        if state.trend_research_validation:
            if state.trend_research_validation.primary_topic_status and not state.trend_research_validation.secondary_topic_status:
                state.trend_research.primary_topic = orig_research.primary_topic
                state.trend_research.primary_topic_reason = orig_research.primary_topic_reason
                state.trend_research.primary_topic_facts = orig_research.primary_topic_facts
            elif state.trend_research_validation.secondary_topic_status and not state.trend_research_validation.primary_topic_status:
                state.trend_research.secondary_topic = orig_research.secondary_topic
                state.trend_research.secondary_topic_reason = orig_research.secondary_topic_reason
                state.trend_research.secondary_topic_facts = orig_research.secondary_topic_facts

        state.prior_topics.add(state.trend_research.primary_topic)
        state.prior_topics.add(state.trend_research.secondary_topic)

        return state

    def flow_condition(self, state: MemeGenState) -> str:
        if state.trend_research.search_tool_call_status:
            return "validator"

        self.logger.warn("Research aborted due to tool call failure.")
        return "end"

    def terminate(self):
        self.tavily_client.save()