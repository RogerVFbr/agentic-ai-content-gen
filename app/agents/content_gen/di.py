from agents.content_gen.agent import ContentGenAgent
from agents.content_gen.controllers.controller import ContentGenController
from agents.content_gen.controllers.worker import ContentGenWorker
from agents.content_gen.core import ContentGenCore
from crosscutting.logging.app_logger import AppLogger
from infrastructure.google_trends_client import GoogleTrendsClient
from infrastructure.serper_dev_client import SerperDevClient


class ContentGenDi:

    @classmethod
    def get_service_collection(cls):
        return [
            AppLogger,
            GoogleTrendsClient,
            SerperDevClient
        ] + [
            ContentGenWorker,
            ContentGenController,
            ContentGenAgent,
            ContentGenCore
        ]

    @classmethod
    def get_pre_instantiated(cls):
        return []