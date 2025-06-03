from typing import Type, Any, Union, Dict

from configurations.configuration_module import ConfigurationModule
from configurations.di_services import AppDi
from crosscutting.logging.app_logger import AppLogger
from crosscutting.service_provider import ServiceCollection


class ConfigurationModuleFactory:

    @staticmethod
    def build(obj: Type[Any], mocks: Union[Dict[Type[Any], Any], ServiceCollection] = None):
        AppLogger.CONFIGS.is_structured = False
        AppLogger.CONFIGS.source_length = 47
        AppLogger.CONFIGS.short_source = True

        module = ConfigurationModule()
        services = AppDi.get_service_collection()

        if mocks:
            if isinstance(mocks, dict):
                for mock_type, mock_instance in mocks.items():
                    services.add_singleton(mock_type, lambda sp: mock_instance)
            elif isinstance(mocks, ServiceCollection):
                services.merge(mocks)

        if module.initialize(services):
            return module.service_provider.get_service(obj)

        raise Exception("Failed to initialize configuration module.")