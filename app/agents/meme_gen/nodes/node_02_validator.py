import copy
import json
import os
from langchain_core.prompts import PromptTemplate
from langgraph.prebuilt import create_react_agent

from agents.meme_gen.nodes.node_base import MemeGenBase
from agents.meme_gen.state import MemeGenState, Validation
from crosscutting.logging.app_logger import AppLogger
from repositories.web_search_repository import WebSearchRepository


class MemeGenTrendValidator(MemeGenBase):

    NODE_NAME = "Validator"

    PROMPTS_FILE = "../prompts.yml"

    def __init__(self,
                 logger: AppLogger,
                 web_search_repository: WebSearchRepository):

        super().__init__(logger)

        self._logger = logger
        self._web_search_repository = web_search_repository

        self._user_prompt = None
        self._agent = None

        self._prompts_file = os.path.join(os.path.dirname(__file__), self.PROMPTS_FILE)

    def initialize(self):
        prompts = self.load_prompts(self._prompts_file, "validator")

        self._user_prompt = PromptTemplate(
            input_variables=["time_now", "research"],
            template=prompts["user"]
        )

        self._agent = create_react_agent(
            model=self.get_llm(),
            prompt=prompts["system"],
            response_format=Validation,
            tools=[self._search_web],
            debug=False
        )

    @AppLogger.timeit()
    async def run(self, state: MemeGenState):
        self._logger.highlight_2(f"Starting {self.NODE_NAME} ...")
        self._web_search_repository.reset_quota(self.NODE_NAME)
        prompt = self._build_prompt(state)

        response = None
        async for step in self._agent.astream(prompt):
            await self.log_progress(step)
            response = step

        state = self._update_state(state, response)
        self._logger.info("Completed.", data=state.validation.__dict__)
        return state

    def _build_prompt(self, state: MemeGenState):
        research = state.research.__dict__.copy()
        del research['tool_call_status']
        del research['tool_call_reason']
        del research['full_topics_list']
        research = json.dumps(research)

        prompt = self._user_prompt.template.format(
            time_now=self.time_now(),
            research=research
        )

        return self.get_user_message(prompt)

    async def _search_web(self, query: str):
        """Executes searches on the web"""
        return await self._web_search_repository.search(self.NODE_NAME, query)

    def _update_state(self, state: MemeGenState, response):
        orig_validation = copy.deepcopy(state.validation) if state.validation else None
        state.validation = self.get_structured_response(response)

        if state.validation.primary_topic_status and not state.validation.secondary_topic_status:
            state.prior_topics.remove(state.research.primary_topic)
        elif not state.validation.primary_topic_status and state.validation.secondary_topic_status:
            state.prior_topics.remove(state.research.secondary_topic)

        state.validation.iterations = orig_validation.iterations + 1 if orig_validation else 1

        return state

    def flow_condition(self, state: MemeGenState) -> str:
        primary_status = state.validation.primary_topic_status
        secondary_status = state.validation.secondary_topic_status

        if primary_status and secondary_status:
            return "editor"

        if state.validation.iterations >= 4:
            self._logger.warn("Research and compliance teams could not get to an agreement.")
            return "end"

        return "researcher"
