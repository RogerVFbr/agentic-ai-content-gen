import json
import os
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from agents.meme_gen.nodes.node_00_base import MemeGenBase
from agents.meme_gen.state import MemeGenState, TrendResearchValidationStatus
from crosscutting.logging.app_logger import AppLogger
from crosscutting.memoize_method import memoize_method
from infrastructure.google_trends_client import GoogleTrendsClient
from infrastructure.serper_dev_client import SerperDevClient


class MemeGenTrendValidator(MemeGenBase):

    NODE_NAME = "TrendResearchValidator"

    PROMPTS_FILE = "../prompts.yml"

    def __init__(self,
                 logger: AppLogger,
                 serper_dev_client: SerperDevClient,
                 google_trends_client: GoogleTrendsClient):

        super().__init__(logger)
        self.logger = logger
        self.google_trends_client = google_trends_client
        self.serper_dev_client = serper_dev_client

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
            model=ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0
            ),
            prompt=self.system_prompt,
            response_format=TrendResearchValidationStatus,
            tools=[
                self.serper_dev_client.search,
                self.thoughts
            ],
            debug=False,
        )

    async def run(self, state: MemeGenState):
        self.logger.highlight_2(f"Starting {self.NODE_NAME} ...")

        iteration = state.trend_research_validation.iterations if state.trend_research_validation else 0

        research = state.trend_research.__dict__.copy()
        del research['search_tool_call_status']
        del research['search_tool_call_reason']
        del research['full_topics_list']
        research = json.dumps(research)

        response = await self.agent.ainvoke(
            self.get_user_message(
                self.user_prompt.template.format(time_now=self.time_now(),research=research))
        )

        state.trend_research_validation = response["structured_response"]
        state.trend_research_validation.iterations = iteration + 1
        self.logger.info("Completed.", data=response["structured_response"].__dict__)
        return state

    def flow_condition(self, state: MemeGenState) -> str:
        primary_status = state.trend_research_validation.primary_topic_status
        secondary_status = state.trend_research_validation.secondary_topic_status

        if primary_status and secondary_status:
            state.trend_research_validation.iterations = 0
            return "end"

        if state.trend_research_validation.iterations >= 2:
            state.trend_research_validation.iterations = 0
            self.logger.warn("Research and compliance teams could not get to an agreement.")
            return "end"

        return "researcher"
