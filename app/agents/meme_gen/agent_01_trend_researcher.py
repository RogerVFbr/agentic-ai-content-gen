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
        self.user_prompt = None
        self.agent = None

    @memoize_method()
    def initialize(self):
        self.system_prompt = """
            You are an expert digital marketing assistant specialized in the fields of humor and comedy.
            """

        self.user_prompt = PromptTemplate(
            input_variables=[],
            template="""
            Your task is to research trending topics by using the Google Trends tool and select amongst the most recent, 
            one that has the most potential for creating a meme with. You will execute your work by strictly following 
            the steps below:

                0. Use the logging tool to publish your thoughts and actions using short sentences.
                1. If you experience failure in any of the tools, abort immediately returning the final structured output with empty or default values.
                2. You must call the Goggle Trends tool provided only a single time to a query for the most recent 
                   trending topics. Do not proceed without having its results first. Use US as the country parameter 
                   value.
                3. You will receive a data about trending topics, and you will select two and only two by performing 
                   the following steps:
                   3.1. Prioritize the ones with higher volume.
                   3.2. You will discard all topics related to politics, crimes, wars, racism, religion, ethnicity, physical 
                        disabilities and natural disasters. You will respect ethics and avoid dark humor.
                   3.3. Additionally, you will discard any topics about sports.
                   3.4. Only if in doubt if a topic should be discarded or not, use the web search to gather more 
                        information about the specific topic only and make an informed decision whether to keep it or 
                        discard it.
                   3.5. Amongst the remaining topics, you will analyze the trends tool's response in detail and select
                        the topics that you think has the most potential for creating a meme.
                   3.6. Make sure the topics you choose can somehow be bound together in a single joke.     
                   3.7. Before you proceed to the next step make sure you have gathered exactly 5 links for each 
                        selected topic. If necessary, search and complement, but minimize the number of calls. 
                        Retrieve an ordered list where fun comes first.    
                   3.7. Return the selected topics as the given structured output.
            """
        )

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
        response = await self.agent.ainvoke(self.get_user_message(self.user_prompt.template))
        self.logger.info("Completed.", data=response["structured_response"].__dict__)
        state.trend_research = response["structured_response"]
        return state