from agents.basic_research.agent import BasicResearchAgent
from agents.basic_research.controllers.controller import BasicResearchController
from agents.basic_research.controllers.worker import BasicResearchWorker
from agents.basic_research.core import BasicResearchCore
from agents.basic_research.graph import BasicResearchGraph
from crosscutting.logging.app_logger import AppLogger
from infrastructure.google_trends_client import GoogleTrendsClient
from infrastructure.serper_dev_client import SerperDevClient


class BasicResearchDi:

    @classmethod
    def get_service_collection(cls):
        return [
            AppLogger,
            GoogleTrendsClient,
            SerperDevClient
        ] + [
            BasicResearchWorker,
            BasicResearchController,
            BasicResearchAgent,
            BasicResearchGraph,
            BasicResearchCore
        ]

    @classmethod
    def get_pre_instantiated(cls):
        return []