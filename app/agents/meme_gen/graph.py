import aiosqlite
import os
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import StateGraph, END

from agents.meme_gen.nodes.node_01_trend_researcher import MemeGenTrendResearcher
from agents.meme_gen.nodes.node_02_trend_research_validator import MemeGenTrendValidator
from agents.meme_gen.state import MemeGenState
from crosscutting.logging.app_logger import AppLogger


class MemeGenGraph:

    MEMORY_FILE = "sql_memory.db"

    def __init__(self,
                 logger: AppLogger,
                 trend_researcher: MemeGenTrendResearcher,
                 trend_research_validator: MemeGenTrendValidator):

        self.logger = logger
        self.trend_researcher = trend_researcher
        self.trend_research_validator = trend_research_validator

        self.conn = None
        self.sql_memory = None

        self.memory_file = os.path.join(os.path.dirname(__file__), "persistence", self.MEMORY_FILE)

    async def build(self):
        await self._initialize_checkpointer()
        self.trend_researcher.initialize()
        self.trend_research_validator.initialize()

        builder = StateGraph(MemeGenState)

        builder.add_node("initializer", self._initialize_state)
        builder.add_node(MemeGenTrendResearcher.NODE_NAME, self.trend_researcher.run)
        builder.add_node(MemeGenTrendValidator.NODE_NAME, self.trend_research_validator.run)

        builder.set_entry_point("initializer")

        builder.add_edge("initializer", MemeGenTrendResearcher.NODE_NAME)

        builder.add_conditional_edges(
            MemeGenTrendResearcher.NODE_NAME,
            self.trend_researcher.flow_condition,
            {
                "validator": MemeGenTrendValidator.NODE_NAME,
                "end": END
            }
        )

        builder.add_conditional_edges(
            MemeGenTrendValidator.NODE_NAME,
            self.trend_research_validator.flow_condition,
            {
                "researcher": MemeGenTrendResearcher.NODE_NAME,
                "end": END
            }
        )

        graph = builder.compile(checkpointer=self.sql_memory)

        return graph

    async def _initialize_checkpointer(self):
        if self.conn:
            return

        memory_dir = os.path.dirname(self.memory_file)
        if not os.path.exists(memory_dir):
            os.makedirs(memory_dir)

        self.conn = await aiosqlite.connect(self.memory_file)
        self.sql_memory = AsyncSqliteSaver(self.conn)

    async def _initialize_state(self, state: MemeGenState):
        self.logger.highlight_2(f"Initializing state.")
        state.trend_research = None
        state.trend_research_validation = None
        return state

    async def terminate(self):
        if self.conn:
            await self.conn.commit()
            await self.conn.close()
            self.conn = None
            self.logger.info("Checkpointer database connection terminated.")
        self.trend_researcher.terminate()
