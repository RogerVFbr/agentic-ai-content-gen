import json
import os
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from agents.meme_gen.agent_00_base import MemeGenBase
from agents.meme_gen.state import MemeGenState, TrendResearch
from crosscutting.logging.app_logger import AppLogger
from crosscutting.memoize_method import memoize_method
from infrastructure.google_trends_client import GoogleTrendsClient
from infrastructure.serper_dev_client import SerperDevClient


class MemeGenTrendResearcher(MemeGenBase):

    NODE_NAME = "TrendResearcher"

    PROMPTS_FILE = "prompts.yml"

    def __init__(self,
                 logger: AppLogger,
                 serper_dev_client:
                 SerperDevClient,
                 google_trends_client: GoogleTrendsClient):

        super().__init__(logger)
        self.logger = logger
        self.google_trends_client = google_trends_client
        self.serper_dev_client = serper_dev_client

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
            input_variables=["time_now", "remake", "prior_topics", "previous_assignment"],
            template=prompts["user"]["main"])

        self.user_remake_prompt = PromptTemplate(
            input_variables=["to_replace", "to_keep"],
            template=prompts["user"]["remake"])

        self.logger.debug("System prompt.", data=self.system_prompt)
        self.logger.debug("User main prompt.", data=self.user_main_prompt.template)
        self.logger.debug("User remake prompt.", data=self.user_remake_prompt.template)

        self.agent = create_react_agent(
            model=ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.7
            ),
            prompt=self.system_prompt,
            response_format=TrendResearch,
            tools=[
                self.google_trends_client.get_trending_now,
                self.serper_dev_client.search,
                self.thoughts
            ],
            debug=False,
        )

    async def run(self, state: MemeGenState):
        prompt = self.build_prompt(state)
        response = await self.agent.ainvoke(self.get_user_message(prompt))
        self.logger.info("Completed.", data=response["structured_response"].__dict__)
        state.trend_research = response["structured_response"]
        state.prior_topics.add(state.trend_research.primary_topic)
        state.prior_topics.add(state.trend_research.secondary_topic)
        return state

    def build_prompt(self, state: MemeGenState):
        prior_topics_str = "No prior topics found."
        previous_assignment_str = "No previous assignments found."
        remake = "-"

        if len(state.prior_topics) > 0:
            prior_topics_str = ", ".join(state.prior_topics)

        self.logger.debug("Prior topics.", data=prior_topics_str)

        validation = state.trend_research_validation

        if validation:
            if not validation.primary_topic_validation_status and validation.secondary_topic_validation_status:
                previous_assignment_str = json.dumps(state.trend_research.__dict__)
                remake = self.user_remake_prompt.format(
                    to_replace="primary",
                    to_keep="secondary",
                )
            if validation.primary_topic_validation_status and not validation.secondary_topic_validation_status:
                previous_assignment_str = json.dumps(state.trend_research.__dict__)
                remake = self.user_remake_prompt.format(
                    to_replace="secondary",
                    to_keep="primary",
                )

        prompt = self.user_main_prompt.format(
            time_now=self.time_now(),
            remake=remake,
            prior_topics=prior_topics_str,
            previous_assignment=previous_assignment_str
        )

        return prompt