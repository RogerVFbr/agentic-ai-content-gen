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
        self.user_prompt = None
        self.agent = None

        self.prompts_file = os.path.join(os.path.dirname(__file__), self.PROMPTS_FILE)

    @memoize_method()
    def initialize(self):
        prompts = self.load_prompts(self.prompts_file)["trend_researcher"]

        self.system_prompt = prompts["system"]

        self.user_prompt = PromptTemplate(
            input_variables=["time_now", "remake", "current_trends", "previous_assignment"],
            template=prompts["user"]["main"]
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

        final_response = None
        async for response in self.agent.astream(self.get_user_message(prompt)):
            await self.log_progress(response)
            final_response = response

        state = self._update_state(state, final_response)
        self.logger.info("Completed.", data=state.trend_research.__dict__)
        return state

    async def build_prompt(self, state: MemeGenState):
        current_trends = await self.google_trends_client.get_trending_now("US", sorted(list(state.prior_topics)))

        prompt = self.user_prompt.format(
            time_now=self.time_now(),
            current_trends=current_trends,
        )

        return prompt

    @staticmethod
    def _update_state(state: MemeGenState, response):
        state.trend_research = response["structured_response"]
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