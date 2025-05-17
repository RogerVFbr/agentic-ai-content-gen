import aiosqlite
import os
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import StateGraph, END

from agents.meme_gen.node_01_trend_researcher import MemeGenTrendResearcher
from agents.meme_gen.node_02_trend_research_validator import MemeGenTrendValidator
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

    def _research_condition(self, state: MemeGenState) -> str:
        if state.trend_research.search_tool_call_status:
            return MemeGenTrendValidator.NODE_NAME

        state.trend_research_validation.iterations = 0
        return END

    def _validator_condition(self, state: MemeGenState) -> str:
        primary_status = state.trend_research_validation.primary_topic_status
        secondary_status = state.trend_research_validation.secondary_topic_status

        if primary_status and secondary_status:
            state.trend_research_validation.iterations = 0
            return END

        if state.trend_research_validation.iterations >= 2:
            state.trend_research_validation.iterations = 0
            self.logger.warn("Research and compliance teams could not get to an agreement.")
            return END

        return MemeGenTrendResearcher.NODE_NAME

    async def build(self):
        await self._initialize_checkpointer()
        self.trend_researcher.initialize()
        self.trend_research_validator.initialize()

        builder = StateGraph(MemeGenState)

        builder.add_node(MemeGenTrendResearcher.NODE_NAME, self.trend_researcher.run)
        builder.add_node(MemeGenTrendValidator.NODE_NAME, self.trend_research_validator.run)

        builder.set_entry_point(MemeGenTrendResearcher.NODE_NAME)
        builder.add_conditional_edges(MemeGenTrendResearcher.NODE_NAME, self._research_condition)
        builder.add_conditional_edges(MemeGenTrendValidator.NODE_NAME, self._validator_condition)

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

    async def terminate(self):
        if self.conn:
            # async with self.conn.execute("SELECT name FROM sqlite_master WHERE type='table';") as cursor:
            #     # Fetch all table names
            #     tables = await cursor.fetchall()
            #
            #     # Print the table names
            #     for table in tables:
            #         print(table[0])
            #
            # # Print the table names
            # for table in tables:
            #     print(table[0])


            await self.conn.commit()
            await self.conn.close()
            self.conn = None
            self.logger.info("Checkpointer database connection terminated.")
