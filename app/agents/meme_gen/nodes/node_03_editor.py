import os

from langchain_core.prompts import PromptTemplate
from langgraph.prebuilt import create_react_agent

from agents.meme_gen.nodes.node_base import MemeGenBase
from agents.meme_gen.state import MemeGenState, Edition
from crosscutting.logging.app_logger import AppLogger
from repositories.image_generation_repository import ImageGenerationRepository


class MemeGenEditor(MemeGenBase):

    NODE_NAME = "Editor"

    PROMPTS_FILE = "../prompts.yml"

    def __init__(self,
                 logger: AppLogger,
                 image_generation_repository: ImageGenerationRepository):

        super().__init__(logger)

        self._logger = logger
        self._image_generation_repository = image_generation_repository

        self._user_prompt = None
        self._agent = None

        self._prompts_file = os.path.join(os.path.dirname(__file__), self.PROMPTS_FILE)

    def initialize(self):
        prompts = self.load_prompts(self._prompts_file)["editor"]

        self._user_prompt = PromptTemplate(
            input_variables=[
                "time_now",
                "primary_topic_name",
                "primary_topic_funny_facts",
                "primary_topic_compliance",
                "secondary_topic_name",
                "secondary_topic_funny_facts",
                "secondary_topic_compliance",
            ],
            template=prompts["user"]
        )

        self._agent = create_react_agent(
            model=self.get_llm(),
            prompt=prompts["system"],
            response_format=Edition,
            tools=[],
            debug=False
        )

    @AppLogger.timeit()
    async def run(self, state: MemeGenState):
        self._logger.highlight_2(f"Starting {self.NODE_NAME} ...")
        prompt = await self._build_prompt(state)

        response = None
        async for step in self._agent.astream(self.get_user_message(prompt)):
            await self.log_progress(step)
            response = step

        state = self._update_state(state, response)
        state.editor.image_url = await self._image_generation_repository.generate(state.editor.prompt)
        self._logger.info(f"Completed.", data=state.editor.__dict__)
        return state

    async def _build_prompt(self, state: MemeGenState):
        return self._user_prompt.format(
            time_now=self.time_now(),
            primary_topic_name=state.research.primary_topic,
            primary_topic_funny_facts=". ".join(state.research.primary_topic_facts),
            primary_topic_compliance=state.validation.primary_topic_reason,
            secondary_topic_name=state.research.secondary_topic,
            secondary_topic_funny_facts=". ".join(state.research.secondary_topic_facts),
            secondary_topic_compliance=state.validation.secondary_topic_reason
        )

    def _update_state(self, state: MemeGenState, response):
        state.editor = self.get_structured_response(response)
        return state

    def flow_condition(self, state: MemeGenState) -> str:
        return "publisher"