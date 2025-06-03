from typing import List, Type, Any, Dict

from agents.meme_gen.agent import MemeGenAgent
from controllers.controller import MemeGenController
from controllers.worker import MemeGenWorker
from agents.meme_gen.graph import MemeGenGraph
from agents.meme_gen.nodes.node_00_initializer import MemeGenInitializer
from agents.meme_gen.nodes.node_01_researcher import MemeGenTrendResearcher
from agents.meme_gen.nodes.node_02_validator import MemeGenTrendValidator
from agents.meme_gen.nodes.node_03_editor import MemeGenEditor
from agents.meme_gen.nodes.node_04_publisher import MemeGenPublisher
from agents.meme_gen.nodes.node_05_failure import MemeGenFailure
from agents.meme_gen.nodes.node_06_success import MemeGenSuccess
from crosscutting.logging.app_logger import AppLogger
from crosscutting.service_provider import ServiceCollection
from infrastructure.google_trends_client import GoogleTrendsClient
from infrastructure.serper_dev_client import SerperDevClient
from infrastructure.tavily_client import TavilyClient
from repositories.web_search_repository import WebSearchRepository
from repositories.web_trends_repository import WebTrendsRepository


class AppDi:

    @classmethod
    def get_service_collection(cls) -> ServiceCollection:
        services = ServiceCollection()

        services.add_singleton(AppLogger)
        services.add_singleton(WebSearchRepository)
        services.add_singleton(WebTrendsRepository)
        services.add_singleton(GoogleTrendsClient)
        services.add_singleton(TavilyClient)
        services.add_singleton(SerperDevClient)

        services.add_singleton(MemeGenWorker)
        services.add_singleton(MemeGenController)
        services.add_singleton(MemeGenAgent)
        services.add_singleton(MemeGenGraph)
        services.add_singleton(MemeGenInitializer)
        services.add_singleton(MemeGenTrendResearcher)
        services.add_singleton(MemeGenTrendValidator)
        services.add_singleton(MemeGenEditor)
        services.add_singleton(MemeGenPublisher)
        services.add_singleton(MemeGenFailure)
        services.add_singleton(MemeGenSuccess)

        return services
