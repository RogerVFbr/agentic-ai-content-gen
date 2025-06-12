import os
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
from repositories.used_topics_repository import UsedTopicsRepository


class MemeGenGraphBuilder:

    def __init__(self,
                 logger: AppLogger,
                 initializer: MemeGenInitializer,
                 researcher: MemeGenTrendResearcher,
                 validator: MemeGenTrendValidator,
                 editor: MemeGenEditor,
                 publisher: MemeGenPublisher,
                 failure: MemeGenFailure,
                 success: MemeGenSuccess,
                 used_topics_repository: UsedTopicsRepository):

        self.logger = logger
        self.initializer = initializer
        self.researcher = researcher
        self.validator = validator
        self.editor = editor
        self.publisher = publisher
        self.failure = failure
        self.success = success
        self.used_topics_repository = used_topics_repository

    async def initialize(self):
        await self.used_topics_repository.load()
        self.researcher.initialize()
        self.validator.initialize()
        self.editor.initialize()

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

        graph = builder.compile()
        self._save_graph_image(graph)
        return graph

    def _save_graph_image(self, graph):
        output_dir = os.path.join(os.path.dirname(__file__), "persistence")
        output_file = os.path.join(output_dir, "memegen_graph.png")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        png_graph = graph.get_graph().draw_mermaid_png()
        with open(output_file, "wb") as f:
            f.write(png_graph)

    async def terminate(self):
        await self.used_topics_repository.flush()
        self.researcher.terminate()
