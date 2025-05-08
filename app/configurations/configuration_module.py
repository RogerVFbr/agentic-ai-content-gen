from configurations.configs import Configs
from crosscutting.app_logger import AppLogger
from configurations.di_container import DiContainer
from configurations.service_collection import ServiceCollection
from dotenv import load_dotenv
import os
import json
import boto3


class ConfigurationModule:

    HAS_INITIALIZED = False

    REQUIRED_ENV_VARS = [
        "APP_ENV",
        "MODEL"
    ]

    @classmethod
    @AppLogger.timeit()
    def initialize(cls) -> bool:

        if cls.HAS_INITIALIZED:
            return True

        try:
            cls.__load_env_vars()
            cls.__configure_logger()
            configs = cls.__load_configs()
            cls.__override_env_vars(configs)
            cls.__build_di_container(configs)
        except Exception as e:
            AppLogger.error(f"Unable to conclude application initialization -> {type(e).__name__}: {e}")
            cls.HAS_INITIALIZED = False
            # raise
            return False

        cls.HAS_INITIALIZED = True
        return True

    @classmethod
    def __load_env_vars(cls) -> None:
        try:
            env_file = os.path.join(os.getcwd(), '.env')
            if not os.path.exists(env_file):
                return

            load_dotenv()

            for key in cls.REQUIRED_ENV_VARS:
                if key not in os.environ:
                    raise ValueError(f"Missing required environment variable: {key}")

            AppLogger.info("Environment variables loaded.")
        except Exception as e:
            AppLogger.error(f"Failed to load environment variables: {e}", exception=e)
            raise

    @classmethod
    def __configure_logger(cls) -> None:
        if "STRUCTURED_LOGS" in os.environ and os.environ["STRUCTURED_LOGS"].lower() == "false":
            AppLogger.STRUCTURED = False

        AppLogger.info("Logger configured.")

    @classmethod
    def __load_configs(cls) -> Configs:
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

    @classmethod
    def __override_env_vars(cls, configs: Configs) -> None:
        """
        Override environment variables with remote credentials if applicable.
        """
        client = None
        overriden_values = []
        try:
            for env_var, param_name in configs.RemoteCredentials.items():
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

    @classmethod
    def __build_di_container(cls, configs: Configs) -> None:
        """
        Build the Dependency Injection container.
        """
        try:
            pre_instantiated = [configs]
            injections = ServiceCollection.get_services()
            DiContainer.build_container(pre_instantiated, injections)
            AppLogger.info("DI container built.")
        except Exception as e:
            AppLogger.error(f"Failed to build DI container: {e}", exception=e)
            raise

    @classmethod
    def get_instance(cls, obj):
        return DiContainer.get(obj)




