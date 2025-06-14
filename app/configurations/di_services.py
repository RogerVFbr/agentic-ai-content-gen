from agents.meme_gen.agent import MemeGenAgent
from agents.meme_gen.graph import MemeGenGraphBuilder
from agents.meme_gen.nodes.node_00_initializer import MemeGenInitializer
from agents.meme_gen.nodes.node_01_researcher import MemeGenTrendResearcher
from agents.meme_gen.nodes.node_02_validator import MemeGenTrendValidator
from agents.meme_gen.nodes.node_03_editor import MemeGenEditor
from agents.meme_gen.nodes.node_04_publisher import MemeGenPublisher
from agents.meme_gen.nodes.node_05_failure import MemeGenFailure
from agents.meme_gen.nodes.node_06_success import MemeGenSuccess
from agents.meme_gen.nodes.node_07_terminate import MemeGenTerminate
from controllers.controller import MemeGenController
from controllers.web_ui import MemeGenWebUi
from controllers.worker import MemeGenWorker
from crosscutting.logging.app_logger import AppLogger
from crosscutting.service_provider import ServiceCollection
from infrastructure.google_trends_client import GoogleTrendsClient
from infrastructure.serper_dev_client import SerperDevClient
from infrastructure.tavily_client import TavilyClient
from repositories.image_generation_repository import ImageGenerationRepository
from repositories.used_topics_repository import UsedTopicsRepository
from repositories.web_search_repository import WebSearchRepository
from repositories.web_trends_repository import WebTrendsRepository


class AppDi:

    @classmethod
    def get_service_collection(cls) -> ServiceCollection:
        services = ServiceCollection()

        services.add_singleton(AppLogger)
        services.add_singleton(GoogleTrendsClient)
        services.add_singleton(TavilyClient)
        services.add_singleton(SerperDevClient)

        services.add_singleton(WebSearchRepository)
        services.add_singleton(WebTrendsRepository)
        services.add_singleton(UsedTopicsRepository)
        services.add_singleton(ImageGenerationRepository)

        services.add_singleton(MemeGenWebUi)
        services.add_singleton(MemeGenWorker)
        services.add_singleton(MemeGenController)
        services.add_singleton(MemeGenAgent)
        services.add_singleton(MemeGenGraphBuilder)
        services.add_singleton(MemeGenInitializer)
        services.add_singleton(MemeGenTrendResearcher)
        services.add_singleton(MemeGenTrendValidator)
        services.add_singleton(MemeGenEditor)
        services.add_singleton(MemeGenPublisher)
        services.add_singleton(MemeGenFailure)
        services.add_singleton(MemeGenSuccess)
        services.add_singleton(MemeGenTerminate)

        return services
