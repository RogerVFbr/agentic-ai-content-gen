from pathlib import Path

from typing import Dict

import boto3
import os
from dotenv import load_dotenv, find_dotenv
import warnings
warnings.warn = lambda *args, **kwargs: None


from configurations.configs import Configs
from configurations.configs_parser import ConfigsParser
from crosscutting.logging.app_logger import AppLogger
from crosscutting.service_provider import ServiceCollection


class ConfigurationModule:

    REQUIRED_ENV_VARS = [
        "APP_ENV",
        "LOGGER_ENV",
        "OPENAI_API_KEY",
        "SERPERDEV_API_KEY",
        "TAVILY_API_KEY",
        "LANGSMITH_TRACING",
        "LANGSMITH_ENDPOINT",
        "LANGSMITH_API_KEY",
        "LANGSMITH_PROJECT",
        "PYTHONWARNINGS",
        "TOKENIZERS_PARALLELISM",
    ]

    def __init__(self):
        self.service_provider = None

    @AppLogger.timeit()
    def initialize(self, service_collection: ServiceCollection) -> bool:
        AppLogger.highlight_1(f"Initializing configuration ...")

        try:
            self._load_env_vars()
            configs = self._load_configs()
            self._override_env_vars(configs.remote_credentials)
            self._validate_env_vars()
            self._build_service_provider(service_collection, configs)
        except Exception as e:
            AppLogger.critical(f"Unable to finish application initialization -> {type(e).__name__}: {e}", exception=e)
            return False

        AppLogger.highlight_1(f"Configuration completed.")
        return True

    def _load_env_vars(self) -> None:
        try:
            dotenv_path = find_dotenv(usecwd=True)

            if dotenv_path:
                load_dotenv(dotenv_path, override=True)
                AppLogger.debug(f"'.env' File environment variables loaded. Path: '{dotenv_path}'.")

            if not os.getenv("APP_ENV"):
                raise ValueError(f"Missing required environment variable: 'APP_ENV'.")

            AppLogger.debug(f"Application environment: '{os.getenv('APP_ENV')}'.")

        except Exception as e:
            AppLogger.error(f"Failed to load or verify environment variables: {e}")
            raise

    def _load_configs(self) -> Configs:
        try:
            parser = ConfigsParser()
            placeholders = {"BASE_DIR": Path(__file__).resolve().parent.parent}
            configs: Configs = Configs(**parser.parse(config_file="configs.json", require_env_override=True))
            configs.mcp.servers = parser.parse(config_file="configs_mcp.json", require_env_override=False, placeholders=placeholders)
            AppLogger.debug("Configs loaded.")
            return configs
        except Exception as e:
            AppLogger.error(f"Failed to load configs: {e}")
            raise

    def _override_env_vars(self, remote_credentials: Dict[str, str]) -> None:
        client = None
        overridden_values = []

        try:
            for env_var, param_name in remote_credentials.items():
                if os.getenv(env_var):
                    continue
                if client is None:
                    client = boto3.client('ssm')
                os.environ[env_var] = client.get_parameter(Name=param_name, WithDecryption=True)['Parameter']['Value']
                overridden_values.append(env_var)

            if overridden_values:
                AppLogger.info(f"Overridden environment variables: {', '.join(overridden_values)}")
        except Exception as e:
            AppLogger.error(f"Failed to override environment variables: {e}")
            raise

    def _validate_env_vars(self) -> None:
        missing_env_vars = []

        for key in self.REQUIRED_ENV_VARS:
            if not os.getenv(key):
                missing_env_vars.append(key)

        if missing_env_vars:
            env_vars = ', '.join(missing_env_vars)
            AppLogger.error(f"Failed to load or verify environment variable(s): {env_vars}.")
            raise ValueError(f"Missing required environment variable(s): {env_vars}")

        AppLogger.debug(f"Environment variables validated.")

    def _build_service_provider(self, service_collection: ServiceCollection, configs: Configs) -> None:
        try:
            service_collection.add_singleton(Configs, lambda _: configs)
            self.service_provider = service_collection.build_service_provider()
            AppLogger.debug("DI container built.")
        except Exception as e:
            AppLogger.error(f"Failed to build DI container: {e}")
            raise