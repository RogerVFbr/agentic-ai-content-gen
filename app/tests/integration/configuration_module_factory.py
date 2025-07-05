from typing import Type, Any, Union, Dict

from src.configurations.configuration_module import ConfigurationModule
from src.configurations.di_services import AppDi
from src.crosscutting.service_provider import ServiceCollection


class ConfigurationModuleFactory:

    @staticmethod
    def build(obj: Type[Any], mocks: Union[Dict[Type[Any], Any], ServiceCollection] = None):
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