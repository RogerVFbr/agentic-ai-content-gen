from agent_crewai.agent import ContentGenAgent
from agent_langgraph.agent import ResearchAgent
from agent_langgraph.graph import ResearchAgentGraph
from agent_langgraph.elements import ResearchAgentElements
from controllers.crewai_controller import CrewAiController
from controllers.langgraph_controller import LangGraphController
from crosscutting.app_logger import AppLogger
from agent_crewai.crew import ContentGen
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