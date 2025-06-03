from typing import Dict, Type, Any

from configurations.configuration_module import ConfigurationModule
from configurations.di_services import AppDi
from crosscutting.logging.app_logger import AppLogger
from crosscutting.service_provider import ServiceCollection


class ConfigurationModuleFactory:

    @staticmethod
    def build(obj: Type[Any], mocks: ServiceCollection = None):
        AppLogger.CONFIGS.is_structured = False
        AppLogger.CONFIGS.source_length = 47
        AppLogger.CONFIGS.short_source = True

        module = ConfigurationModule()
        services = AppDi.get_service_collection()

        if mocks:
            services.merge(mocks)

        if module.initialize(services):
            component = module.service_provider.get_service(obj)
            return component
        raise Exception("Failed to initialize configuration module.")