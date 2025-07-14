import os

from langchain_core.prompts import PromptTemplate
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

from agents.meme_gen.nodes.node_base import MemeGenBase
from agents.meme_gen.state import MemeGenState, Publisher
from configurations.configs import Configs
from crosscutting.logging.app_logger import AppLogger


class MemeGenPublisher(MemeGenBase):

    NODE_NAME = "Publisher"

    PROMPTS_FILE = "../prompts.yml"

    def __init__(self,
                 logger: AppLogger,
                 configs: Configs,
                 client: MultiServerMCPClient):

        super().__init__(logger)

        self._logger = logger
        self._configs = configs
        self._mcp_client = client

        self._user_prompt = None
        self._agent_factory = None

        self._prompts_file = os.path.join(os.path.dirname(__file__), self.PROMPTS_FILE)

    def initialize(self):
        prompts = self.load_prompts(self._prompts_file, "publisher")

        self._user_prompt = PromptTemplate(
            input_variables=[
                "message",
                "image_path"
            ],
            template=prompts["user"]
        )

        self._agent_factory = lambda tools: create_react_agent(
            model=self.get_llm(),
            prompt=prompts["system"],
            response_format=Publisher,
            tools=tools,
            debug=self._configs.flags.agent_log_verbose
        )

    @AppLogger.timeit()
    async def run(self, state: MemeGenState):
        self._logger.highlight_2(f"Starting {self.NODE_NAME} ...")
        prompt = await self._build_prompt(state)

        async with self._mcp_client.session("social_networks") as session:
            tools = await load_mcp_tools(session)
            agent = self._agent_factory(tools)

            response = None
            async for step in agent.astream(prompt):
                await self.log_progress(step)
                response = step

        state = await self._update_state(state, response)
        self._logger.info("Completed.", data=state.publisher.__dict__)
        return state

    async def _build_prompt(self, state: MemeGenState):
        prompt = self._user_prompt.format(
            message=state.editor.message,
            image_path=state.editor.image_url
        )

        return self.get_user_message(prompt)

    async def _update_state(self, state: MemeGenState, response):
        state.publisher = self.get_structured_response(response)
        return state

    def flow_condition(self, state: MemeGenState) -> str:
        return "end"