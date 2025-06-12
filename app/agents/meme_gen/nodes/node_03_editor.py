import os

from langchain_core.prompts import PromptTemplate
from langgraph.prebuilt import create_react_agent

from agents.meme_gen.nodes.node_base import MemeGenBase
from agents.meme_gen.state import MemeGenState, TrendResearchEditor
from crosscutting.logging.app_logger import AppLogger


class MemeGenEditor(MemeGenBase):

    NODE_NAME = "Editor"

    PROMPTS_FILE = "../prompts.yml"

    def __init__(self,
                 logger: AppLogger):

        super().__init__(logger)

        self.logger = logger

        self.system_prompt = None
        self.user_prompt = None
        self.agent = None

        self.prompts_file = os.path.join(os.path.dirname(__file__), self.PROMPTS_FILE)

    def initialize(self):
        prompts = self.load_prompts(self.prompts_file)["editor"]

        self.system_prompt = prompts["system"]

        self.user_prompt = PromptTemplate(
            input_variables=[
                "time_now",
                "primary_topic_name",
                "primary_topic_funny_facts",
                "primary_topic_compliance",
                "secondary_topic_name",
                "secondary_topic_funny_facts",
                "secondary_topic_compliance",
            ],
            template=prompts["user"])

        self.agent = create_react_agent(
            model=self.get_llm(),
            prompt=self.system_prompt,
            response_format=TrendResearchEditor,
            tools=[],
            debug=False)

    @AppLogger.timeit()
    async def run(self, state: MemeGenState):
        self.logger.highlight_2(f"Starting {self.NODE_NAME} ...")
        prompt = await self._build_prompt(state)

        response = None
        async for step in self.agent.astream(self.get_user_message(prompt)):
            await self.log_progress(step)
            response = step

        state = self._update_state(state, response)
        self.logger.info(f"Completed.", data=state.editor.__dict__)
        return state

    async def _build_prompt(self, state: MemeGenState):
        return self.user_prompt.format(
            time_now=self.time_now(),
            primary_topic_name=state.trend_research.primary_topic,
            primary_topic_funny_facts=". ".join(state.trend_research.primary_topic_facts),
            primary_topic_compliance=state.trend_research_validation.primary_topic_reason,
            secondary_topic_name=state.trend_research.secondary_topic,
            secondary_topic_funny_facts=". ".join(state.trend_research.secondary_topic_facts),
            secondary_topic_compliance=state.trend_research_validation.secondary_topic_reason)

    def _update_state(self, state: MemeGenState, response):
        state.editor = self.get_structured_response(response)
        return state

    def flow_condition(self, state: MemeGenState) -> str:
        return "publisher"