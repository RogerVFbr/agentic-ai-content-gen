import asyncio
import boto3
import os
from dotenv import load_dotenv

from configurations.configs import Configs
from configurations.configs_parser import ConfigsParser
from crosscutting.logging.app_logger import AppLogger
from crosscutting.service_provider import ServiceCollection


class ConfigurationModule:

    REQUIRED_ENV_VARS = [
        "APP_ENV",
        "LOGGER_ENV",
        "MODEL",
        "OPENAI_API_KEY",
        "SERPERDEV_API_KEY",
        "TAVILY_API_KEY",
        "LANGSMITH_TRACING",
        "LANGSMITH_ENDPOINT",
        "LANGSMITH_API_KEY",
        "LANGSMITH_PROJECT"
    ]

    def __init__(self):
        self.service_provider = None

    def run(self, service_collection, obj, callback):
        async def execute():
            module = ConfigurationModule()
            if module.initialize(service_collection):
                instance = module.service_provider.get_service(obj)
                await callback(instance)

        asyncio.run(execute())

    @AppLogger.timeit()
    def initialize(self, service_collection: ServiceCollection) -> bool:
        AppLogger.highlight_1(f"Initializing configuration ...")

        try:
            self._load_env_vars()
            configs = self._load_configs()
            service_collection.add_singleton(Configs, lambda sp: configs)
            self._override_env_vars(configs)
            self._validate_env_vars()
            self._build_di_container(service_collection)
        except Exception as e:
            AppLogger.critical(f"Unable to finish application initialization -> {type(e).__name__}: {e}", exception=e)
            return False

        AppLogger.highlight_1(f"Configuration completed.")
        return True

    def _load_env_vars(self) -> None:
        try:
            current_dir = os.path.abspath(os.path.dirname(__file__))

            for _ in range(5):
                env_path = os.path.join(current_dir, ".env")
                if os.path.exists(env_path):
                    load_dotenv(env_path)
                    AppLogger.debug(f"'.env' File environment variables loaded. Path: '{env_path}'.")
                    break
                current_dir = os.path.dirname(current_dir)

            if "APP_ENV" not in os.environ or len(os.environ["APP_ENV"]) == 0:
                raise ValueError(f"Missing required environment variable: 'APP_ENV'.")

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

    def _validate_env_vars(self) -> None:
        for key in self.REQUIRED_ENV_VARS:
            if key not in os.environ or len(os.environ[key]) == 0:
                AppLogger.error(f"Failed to load or verify environment variable: '{key}'.")
                raise ValueError(f"Missing required environment variable: {key}")

        AppLogger.debug(f"Environment variables validated.")

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