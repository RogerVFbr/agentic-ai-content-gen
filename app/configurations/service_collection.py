from agents.content_gen.agent import ContentGenAgent
from agents.content_gen.core import ContentGenCore
from agents.basic_research.agent import BasicResearchAgent
from agents.basic_research.core import BasicResearchCore
from agents.basic_research.graph import BasicResearchGraph
from agents.content_gen.controllers.controller import ContentGenController
from agents.basic_research.controllers.controller import BasicResearchController
from agents.meme_gen.agent import MemeGenAgent
from agents.meme_gen.agent_trend_researcher import MemeGenTrendResearcher
from agents.meme_gen.controllers.controller import MemeGenController
from agents.meme_gen.controllers.worker import MemeGenWorker
from agents.meme_gen.graph import MemeGenGraph
from crosscutting.logging.app_logger import AppLogger
from agents.content_gen.controllers.worker import ContentGenWorker
from agents.basic_research.controllers.worker import BasicResearchWorker
from infrastructure.google_trends_client import GoogleTrendsClient
from infrastructure.serper_dev_client import SerperDevClient


class ServiceCollection:

    @classmethod
    def get_services(cls):
        return [
            AppLogger,
            GoogleTrendsClient,
            SerperDevClient
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
        ] + [
            MemeGenWorker,
            MemeGenController,
            MemeGenAgent,
            MemeGenGraph,
            MemeGenTrendResearcher
        ]