from typing import Dict, Type, Any

from configurations.configuration_module import ConfigurationModule
from configurations.di_services import AppDi
from crosscutting.logging.app_logger import AppLogger


class ConfigurationModuleFactory:

    @staticmethod
    def build(obj: Type[Any], mocks: Dict[Type[Any], Any] = None):
        AppLogger.CONFIGS.is_structured = False
        AppLogger.CONFIGS.source_length = 47
        AppLogger.CONFIGS.short_source = True
        module = ConfigurationModule()
        pre_instantiated = AppDi.get_pre_instantiated()

        if mocks:
            for target, mock in mocks.items():
                pre_instantiated[target] = mock

        service_collection = AppDi.get_service_collection()
        if module.initialize(pre_instantiated, service_collection):
            component = module.di_container.get(obj)
            return component
        raise Exception("Failed to initialize configuration module.")