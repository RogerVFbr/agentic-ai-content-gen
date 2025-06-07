import aiosqlite
import os
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import StateGraph, END

from agents.meme_gen.nodes.node_00_initializer import MemeGenInitializer
from agents.meme_gen.nodes.node_01_researcher import MemeGenTrendResearcher
from agents.meme_gen.nodes.node_02_validator import MemeGenTrendValidator
from agents.meme_gen.nodes.node_03_editor import MemeGenEditor
from agents.meme_gen.nodes.node_04_publisher import MemeGenPublisher
from agents.meme_gen.nodes.node_05_failure import MemeGenFailure
from agents.meme_gen.nodes.node_06_success import MemeGenSuccess
from agents.meme_gen.state import MemeGenState
from crosscutting.logging.app_logger import AppLogger


class MemeGenGraphBuilder:

    MEMORY_FILE = "sql_memory.db"

    def __init__(self,
                 logger: AppLogger,
                 initializer: MemeGenInitializer,
                 researcher: MemeGenTrendResearcher,
                 validator: MemeGenTrendValidator,
                 editor: MemeGenEditor,
                 publisher: MemeGenPublisher,
                 failure: MemeGenFailure,
                 success: MemeGenSuccess):

        self.logger = logger

        self.initializer = initializer
        self.researcher = researcher
        self.validator = validator
        self.editor = editor
        self.publisher = publisher
        self.failure = failure
        self.success = success

        self.conn = None
        self.sql_memory = None

        self.memory_file = os.path.join(os.path.dirname(__file__), "persistence", self.MEMORY_FILE)

    async def initialize(self):
        await self._initialize_checkpointer()
        self.researcher.initialize()
        self.validator.initialize()

    async def build(self):
        builder = StateGraph(MemeGenState)

        builder.add_node(MemeGenInitializer.NODE_NAME, self.initializer.run)
        builder.add_node(MemeGenTrendResearcher.NODE_NAME, self.researcher.run)
        builder.add_node(MemeGenTrendValidator.NODE_NAME, self.validator.run)
        builder.add_node(MemeGenEditor.NODE_NAME, self.editor.run)
        builder.add_node(MemeGenPublisher.NODE_NAME, self.publisher.run)
        builder.add_node(MemeGenFailure.NODE_NAME, self.failure.run)
        builder.add_node(MemeGenSuccess.NODE_NAME, self.success.run)

        builder.set_entry_point(MemeGenInitializer.NODE_NAME)

        builder.add_edge(MemeGenInitializer.NODE_NAME, MemeGenTrendResearcher.NODE_NAME)
        builder.add_edge(MemeGenFailure.NODE_NAME, END)
        builder.add_edge(MemeGenSuccess.NODE_NAME, END)

        builder.add_conditional_edges(
            MemeGenTrendResearcher.NODE_NAME,
            self.researcher.flow_condition,
            {
                "validator": MemeGenTrendValidator.NODE_NAME,
                "end": MemeGenFailure.NODE_NAME
            }
        )

        builder.add_conditional_edges(
            MemeGenTrendValidator.NODE_NAME,
            self.validator.flow_condition,
            {
                "researcher": MemeGenTrendResearcher.NODE_NAME,
                "editor": MemeGenEditor.NODE_NAME,
                "end": MemeGenFailure.NODE_NAME
            }
        )

        builder.add_conditional_edges(
            MemeGenEditor.NODE_NAME,
            self.editor.flow_condition,
            {
                "publisher": MemeGenPublisher.NODE_NAME,
                "end": MemeGenFailure.NODE_NAME
            }
        )

        builder.add_conditional_edges(
            MemeGenPublisher.NODE_NAME,
            self.publisher.flow_condition,
            {
                "end": MemeGenSuccess.NODE_NAME
            }
        )

        graph = builder.compile(checkpointer=self.sql_memory)
        self._save_graph_image(graph)
        return graph

    async def _initialize_checkpointer(self):
        if self.conn:
            return

        memory_dir = os.path.dirname(self.memory_file)
        if not os.path.exists(memory_dir):
            os.makedirs(memory_dir)

        self.conn = await aiosqlite.connect(self.memory_file)
        self.sql_memory = AsyncSqliteSaver(self.conn)

    def _save_graph_image(self, graph):
        output_dir = os.path.join(os.path.dirname(__file__), "persistence")
        output_file = os.path.join(output_dir, "memegen_graph.png")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        png_graph = graph.get_graph().draw_mermaid_png()
        with open(output_file, "wb") as f:
            f.write(png_graph)

    async def terminate(self):
        if self.conn:
            await self.conn.commit()
            await self.conn.close()
            self.conn = None
            self.logger.info("Checkpointer database connection terminated.")
        self.researcher.terminate()
