import json
import os
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from agents.meme_gen.agent_00_base import MemeGenBase
from agents.meme_gen.state import MemeGenState, TrendResearchValidationStatus
from crosscutting.logging.app_logger import AppLogger
from crosscutting.memoize_method import memoize_method
from infrastructure.google_trends_client import GoogleTrendsClient
from infrastructure.serper_dev_client import SerperDevClient


class MemeGenTrendValidator(MemeGenBase):

    PROMPTS_FILE = "prompts.yml"

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
            input_variables=["research"],
            template=prompts["user"]
        )

        self.logger.debug("System prompt.", data=self.system_prompt)
        self.logger.debug("User prompt.", data=self.user_prompt.template)

        self.agent = create_react_agent(
            model=ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.7
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

        research = state.trend_research.__dict__
        del research['trends_tool_call_status']
        del research['trends_tool_call_reason']
        del research['search_tool_call_status']
        del research['search_tool_call_reason']
        del research['full_topics_list']
        research = json.dumps(research)

        response = await self.agent.ainvoke(self.get_user_message(self.user_prompt.template.format(research=research)))

        self.logger.info("Completed.", data=response["structured_response"].__dict__)
        state.trend_research_validation_history.history.append(response["structured_response"])
        return state