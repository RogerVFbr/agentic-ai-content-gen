import os

from agents.meme_gen.agent import MemeGenAgent
from agents.meme_gen.controllers.controller import MemeGenController
from agents.meme_gen.controllers.worker import MemeGenWorker
from agents.meme_gen.graph import MemeGenGraph
from agents.meme_gen.nodes.node_01_trend_researcher import MemeGenTrendResearcher
from agents.meme_gen.nodes.node_02_trend_research_validator import MemeGenTrendValidator
from crosscutting.logging.app_logger import AppLogger
from infrastructure.google_trends_client import GoogleTrendsClient
from infrastructure.serper_dev_client import SerperDevClient
from infrastructure.tavily_client import TavilyClient


class MemeGenDi:

    TAVILY_CACHE_PATH = os.path.join(os.path.dirname(__file__), "persistence", "tavily_cache.pkl")
    SERPER_DEV_CACHE_PATH = os.path.join(os.path.dirname(__file__), "persistence", "serper_dev_cache.pkl")

    @classmethod
    def get_service_collection(cls):
        return [
            GoogleTrendsClient
        ] + [
            MemeGenWorker,
            MemeGenController,
            MemeGenAgent,
            MemeGenGraph,
            MemeGenTrendResearcher,
            MemeGenTrendValidator
        ]

    @classmethod
    def get_pre_instantiated(cls):
        logger = AppLogger()
        tavily_client = TavilyClient(cls.TAVILY_CACHE_PATH, logger)
        serper_dev_client = SerperDevClient(cls.SERPER_DEV_CACHE_PATH, logger)
        return [logger, tavily_client, serper_dev_client]