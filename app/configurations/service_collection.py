from controllers.app_controller import AppController
from crosscutting.app_logger import AppLogger
from agent.crew import ContentGen


class ServiceCollection:

    @classmethod
    def get_services(cls):
        return [
            AppController,
            AppLogger,
            ContentGen
        ]