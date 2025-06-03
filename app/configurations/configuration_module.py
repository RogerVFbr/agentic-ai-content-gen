import asyncio
import boto3
import os
from dotenv import load_dotenv

from configurations.configs import Configs
from configurations.configs_parser import ConfigsParser
from crosscutting.logging.app_logger import AppLogger
from crosscutting.memoize_method import memoize_method
from crosscutting.service_provider import ServiceCollection


class ConfigurationModule:

    REQUIRED_ENV_VARS = [
        "APP_ENV",
        "MODEL"
    ]

    def __init__(self):
        self.service_provider = None

    def run(self, service_collection, obj, callback):
        async def execute():
            module = self._get()
            if module.initialize(service_collection):
                instance = module.service_provider.get_service(obj)
                await callback(instance)

        asyncio.run(execute())

    @classmethod
    @memoize_method()
    def _get(cls):
        return ConfigurationModule()

    # @memoize_method()
    @AppLogger.timeit()
    def initialize(self, service_collection: ServiceCollection) -> bool:
        AppLogger.highlight_1(f"Initializing configuration ...")

        try:
            self._load_env_vars()
            configs = self._load_configs()
            service_collection.add_singleton(Configs, lambda sp: configs)
            self._override_env_vars(configs)
            self._build_di_container(service_collection)
        except Exception as e:
            AppLogger.critical(f"Unable to finish application initialization -> {type(e).__name__}: {e}", exception=e)
            return False

        AppLogger.highlight_1(f"Configuration completed.")
        return True

    def _load_env_vars(self) -> None:
        try:
            env_file = os.path.join(os.getcwd(), '.env')

            if os.path.isfile(env_file):
                load_dotenv()
                AppLogger.debug("'.env' File environment variables loaded.")

            for key in self.REQUIRED_ENV_VARS:
                if key not in os.environ:
                    raise ValueError(f"Missing required environment variable: {key}")

        except Exception as e:
            AppLogger.error(f"Failed to load or verify environment variables: {e}", exception=e)
            raise

    def _load_configs(self) -> Configs:
        try:
            configs = ConfigsParser().parse()
            AppLogger.debug("Configs loaded.")
            return configs
        except Exception as e:
            AppLogger.error(f"Failed to load configs: {e}", exception=e)
            raise

    def _override_env_vars(self, configs: Configs) -> None:
        """
        Override environment variables with remote credentials if applicable.
        """
        client = None
        overridden_values = []
        try:
            for env_var, param_name in configs.remote_credentials.items():
                if env_var in os.environ and os.environ[env_var]:
                    continue
                if client is None:
                    client = boto3.client('ssm')
                value = client.get_parameter(Name=param_name, WithDecryption=True)['Parameter']['Value']
                os.environ[env_var] = value
                overridden_values.append(env_var)

            if overridden_values:
                AppLogger.info(f"Overridden environment variables: {', '.join(overridden_values)}")
        except Exception as e:
            AppLogger.error(f"Failed to override environment variables: {e}", exception=e)
            raise

    def _build_di_container(self, service_collection: ServiceCollection) -> None:
        """
        Build the Dependency Injection container.
        """
        try:
            self.service_provider = service_collection.build_service_provider()
            AppLogger.debug("DI container built.")
        except Exception as e:
            AppLogger.error(f"Failed to build DI container: {e}", exception=e)
            raise