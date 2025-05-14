import asyncio
import boto3
import os
from dotenv import load_dotenv
from typing import List

from configurations.configs import Configs
from configurations.configs_parser import ConfigsParser
from configurations.di_container import DiContainer
from configurations.service_collection import ServiceCollection
from crosscutting.logging.app_logger import AppLogger
from crosscutting.memoize_method import memoize_method


class ConfigurationModule:

    REQUIRED_ENV_VARS = [
        "APP_ENV",
        "MODEL"
    ]

    @classmethod
    def run(cls, obj, callback):
        async def execute():
            module = cls._get()
            if module._initialize():
                instance = DiContainer.get(obj)
                await callback(instance)

        asyncio.run(execute())

    @classmethod
    @memoize_method()
    def _get(cls):
        return ConfigurationModule()

    @memoize_method()
    @AppLogger.timeit()
    def _initialize(self) -> bool:
        AppLogger.highlight(f"Initializing configuration ...")

        try:
            self._load_env_vars()
            configs = self._load_configs()
            self._override_env_vars(configs)
            pre_instantiated = self._pre_instantiate(configs)
            self._build_di_container(pre_instantiated)
        except Exception as e:
            AppLogger.critical(f"Unable to finish application initialization -> {type(e).__name__}: {e}")
            return False

        AppLogger.highlight(f"Configuration completed.")
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
        overriden_values = []
        try:
            for env_var, param_name in configs.remote_credentials.items():
                if env_var in os.environ and os.environ[env_var]:
                    continue
                if client is None:
                    client = boto3.client('ssm')
                value = client.get_parameter(Name=param_name, WithDecryption=True)['Parameter']['Value']
                os.environ[env_var] = value
                overriden_values.append(env_var)

            if overriden_values:
                AppLogger.info(f"Overridden environment variables: {', '.join(overriden_values)}")
        except Exception as e:
            AppLogger.error(f"Failed to override environment variables: {e}", exception=e)
            raise

    def _pre_instantiate(self, configs: Configs) -> List[object]:
        try:
            AppLogger.debug(f"Pre instantiation complete.")
            return [configs]
        except Exception as e:
            AppLogger.error(f"Unable to preinstantiate: {e}", exception=e)
            raise

    def _build_di_container(self, pre_instantiated) -> None:
        """
        Build the Dependency Injection container.
        """
        try:
            injections = ServiceCollection.get_services()
            DiContainer.build_container(pre_instantiated, injections)
            AppLogger.debug("DI container built.")
        except Exception as e:
            AppLogger.error(f"Failed to build DI container: {e}", exception=e)
            raise