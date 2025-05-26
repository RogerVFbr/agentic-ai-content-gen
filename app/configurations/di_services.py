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
from infrastructure.google_trends_client import GoogleTrendsClient
from infrastructure.serper_dev_client import SerperDevClient
from infrastructure.tavily_client import TavilyClient
from repositories.web_search_repository import WebSearchRepository


class MemeGenDi:

    @classmethod
    def get_service_collection(cls):
        return [
            AppLogger,
            GoogleTrendsClient,
            WebSearchRepository,
            TavilyClient,
            SerperDevClient
        ] + [
            MemeGenWorker,
            MemeGenController,
            MemeGenAgent,
            MemeGenGraph,
            MemeGenInitializer,
            MemeGenTrendResearcher,
            MemeGenTrendValidator,
            MemeGenEditor,
            MemeGenPublisher,
            MemeGenFailure,
            MemeGenSuccess
        ]

    @classmethod
    def get_pre_instantiated(cls):
        return []