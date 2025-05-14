from agents.content_gen.agent import ContentGenAgent
from agents.content_gen.crew import ContentGenCore
from agents.basic_research.agent import BasicResearchAgent
from agents.basic_research.elements import BasicResearchCore
from agents.basic_research.graph import BasicResearchGraph
from agents.content_gen.controllers.controller import ContentGenController
from agents.basic_research.controllers.controller import BasicResearchController
from crosscutting.logging.app_logger import AppLogger
from agents.content_gen.controllers.worker import ContentGenWorker
from agents.basic_research.controllers.worker import BasicResearchWorker


class ServiceCollection:

    @classmethod
    def get_services(cls):
        return [
            AppLogger
        ] + [
            ContentGenWorker,
            ContentGenController,
            ContentGenAgent,
            ContentGenCore
        ] + [
            BasicResearchWorker,
            BasicResearchController,
            BasicResearchAgent,
            BasicResearchGraph,
            BasicResearchCore
        ]