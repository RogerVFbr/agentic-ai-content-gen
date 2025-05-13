from agents.crewai.agent import ContentGenAgent
from agents.crewai.crew import ContentGen
from agents.langgraph.agent import ResearchAgent
from agents.langgraph.elements import ResearchAgentElements
from agents.langgraph.graph import ResearchAgentGraph
from controllers.crewai_controller import CrewAiController
from controllers.langgraph_controller import LangGraphController
from crosscutting.logging.app_logger import AppLogger
from workers.crewai_worker import CrewAiWorker
from workers.langgraph_worker import LangGraphWorker


class ServiceCollection:

    @classmethod
    def get_services(cls):
        return [
            AppLogger
        ] + [
            CrewAiWorker,
            CrewAiController,
            ContentGenAgent,
            ContentGen
        ] + [
            LangGraphWorker,
            LangGraphController,
            ResearchAgent,
            ResearchAgentGraph,
            ResearchAgentElements
        ]