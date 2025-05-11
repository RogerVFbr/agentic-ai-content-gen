from agent_langgraph.agent import ResearchAgent
from agent_langgraph.graph import ResearchAgentGraph
from agent_langgraph.elements import ResearchAgentElements
from controllers.langgraph_controller import LangGraphController
from crosscutting.app_logger import AppLogger
from agent_crewai.crew import ContentGen
from crosscutting.graceful_shutdown import GracefulShutdown


class ServiceCollection:

    @classmethod
    def get_services(cls):
        return [
            LangGraphController,
            AppLogger,
            ContentGen,
            GracefulShutdown
        ] + [
            ResearchAgent,
            ResearchAgentElements,
            ResearchAgentGraph
        ]