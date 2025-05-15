import json

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from agents.meme_gen.agent_00_base import MemeGenBase
from agents.meme_gen.state import MemeGenState, TrendResearch, TrendResearchValidationStatus
from crosscutting.logging.app_logger import AppLogger
from crosscutting.memoize_method import memoize_method
from infrastructure.google_trends_client import GoogleTrendsClient
from infrastructure.serper_dev_client import SerperDevClient


class MemeGenTrendValidator(MemeGenBase):

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

    @memoize_method()
    def initialize(self):
        self.system_prompt = """
            You are an expert lawyer and ethics advisor who has extensively worked in compliance sectors of marketing 
            companies. You are now working for an agency specialized in producing humor and memes. 
            """

        self.user_prompt = PromptTemplate(
            input_variables=["research"],
            template="""
            Your task is to analyze topics chosen by the research team which are displayed in the CHOSEN TOPICS DATA 
            section to be used on the company's next meme. The final output of your analysis will be to determine 
            whether the chosen topics are legally, ethical and morally acceptable. You will execute your work by 
            strictly following the steps below:

                0. Use the logging tool to publish your thoughts and actions using short sentences.
                1. If you experience failure in any of the tools, abort immediately returning the final structured 
                   output with empty or default values.
                2. You must carefully analyze the given topics, the reason they were chosen, and if necessary, look for
                   clarifications on the internet. Make sure to consider recent facts on your analysis.
                3. You must identify if any of the found topics is related to the following sensitive subjects:
                   3.1. Politics
                   3.2. War
                   3.3. Racism
                   3.4. Religion
                   3.5. Ethnicity
                   3.6. Physical disabilities
                   3.7. Natural disasters
                   3.8. Any other subject that may cause harm or offend other people.
                4. Return the final structured output with your final decision and reasoning.
                
            # CHOSEN TOPICS DATA
            
            {research}
            """
        )

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