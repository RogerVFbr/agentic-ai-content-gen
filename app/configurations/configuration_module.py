from typing import List

import logging

from agent.crew import ContentGen
from configurations.configs import Configs
from crosscutting.app_logger import AppLogger
from configurations.di_container import DiContainer
from configurations.service_collection import ServiceCollection
from dotenv import load_dotenv
import os
import json
import boto3


class ConfigurationModule:

    INSTANCE = None

    HAS_INITIALIZED = False

    REQUIRED_ENV_VARS = [
        "APP_ENV",
        "MODEL"
    ]

    @classmethod
    def get(cls):
        if cls.INSTANCE is None:
            cls.INSTANCE = ConfigurationModule()
        return cls.INSTANCE


    @AppLogger.timeit()
    def initialize(self) -> bool:
        if self.HAS_INITIALIZED:
            return True
        try:
            self.__load_env_vars()
            self.__configure_logger()
            configs = self.__load_configs()
            self.__override_env_vars(configs)
            pre_instantiated = self.__pre_instantiate(configs)
            self.__build_di_container(pre_instantiated)
        except Exception as e:
            AppLogger.error(f"Unable to conclude application initialization -> {type(e).__name__}: {e}")
            self.HAS_INITIALIZED = False
            # raise
            return False

        self.HAS_INITIALIZED = True
        return True

    def __load_env_vars(self) -> None:
        try:
            env_file = os.path.join(os.getcwd(), '.env')

            if os.path.isfile(env_file):
                load_dotenv()
                AppLogger.info("Environment variables loaded.")

            for key in self.REQUIRED_ENV_VARS:
                if key not in os.environ:
                    raise ValueError(f"Missing required environment variable: {key}")

        except Exception as e:
            AppLogger.error(f"Failed to load environment variables: {e}", exception=e)
            raise

    def __configure_logger(self) -> None:
        if "STRUCTURED_LOGS" in os.environ and os.environ["STRUCTURED_LOGS"].lower() == "false":
            AppLogger.STRUCTURED = False

        logging.getLogger("crewai").setLevel(logging.CRITICAL)

        AppLogger.info("Logger configured.")

    def __load_configs(self) -> Configs:
        def merge_configs(base: dict, override: dict) -> dict:
            for key, value in override.items():
                if key in base:
                    if isinstance(base[key], dict) and isinstance(value, dict):
                        merge_configs(base[key], value)
                    elif isinstance(base[key], list) and isinstance(value, list):
                        base[key] = value
                    else:
                        base[key] = value
                else:
                    base[key] = value
            return base

        try:
            env = os.getenv('APP_ENV')

            base_config_file = f'{os.getcwd()}/configs.json'
            env_config_file = f'{os.getcwd()}/configs.{env}.json'

            if not os.path.exists(base_config_file):
                raise FileNotFoundError(f"Configuration file '{base_config_file}'")

            if not os.path.exists(env_config_file):
                raise FileNotFoundError(f"Configuration file '{env_config_file}'")

            with open(base_config_file, 'r') as file:
                config = json.load(file)

            if os.path.exists(env_config_file):
                with open(env_config_file, 'r') as file:
                    env_config = json.load(file)
                config = merge_configs(config, env_config)

            AppLogger.info("Configs loaded.")
            return Configs(**config)
        except Exception as e:
            AppLogger.error(f"Failed to load configs: {e}", exception=e)
            raise

    def __override_env_vars(self, configs: Configs) -> None:
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

    def __pre_instantiate(self, configs: Configs) -> List[object]:
        try:
            agent = ContentGen(configs)

            AppLogger.info(f"Pre instantiation complete.")
            return [configs, agent]
        except Exception as e:
            AppLogger.error(f"Unable to preinstantiate: {e}", exception=e)
            raise

    def __build_di_container(self, pre_instantiated) -> None:
        """
        Build the Dependency Injection container.
        """
        try:
            injections = ServiceCollection.get_services()
            DiContainer.build_container(pre_instantiated, injections)
            AppLogger.info("DI container built.")
        except Exception as e:
            AppLogger.error(f"Failed to build DI container: {e}", exception=e)
            raise

    def get_instance(self, obj):
        return DiContainer.get(obj)




