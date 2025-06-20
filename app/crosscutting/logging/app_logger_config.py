import json
import os
from dotenv import load_dotenv, find_dotenv
from enum import Enum
from pydantic import BaseModel


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AppLoggerConfig(BaseModel):
    is_structured: bool = True
    short_source: bool = False
    header_size: int = 80
    source_length: int = None
    min_level: LogLevel = LogLevel.DEBUG
    min_level_by_prefix: dict[str, LogLevel] = {}


class AppLoggerConfigsParser:

    ENVIRONMENT_ENV_VAR = 'LOGGER_ENV'
    CONFIG_FILE = 'configs_logger.json'
    SEARCH_LEVELS = 10

    @classmethod
    def parse(cls) -> AppLoggerConfig:
        try:
            load_dotenv(find_dotenv(usecwd=True), override=True)
            base_config_file, env_config_file = cls._find_files()

            if os.path.exists(base_config_file):
                with open(base_config_file, 'r') as file:
                    config = json.load(file)
            else:
                return AppLoggerConfig()

            if os.path.exists(env_config_file):
                with open(env_config_file, 'r') as file:
                    env_config = json.load(file)
                config = cls._merge_configs(config, env_config)

            return AppLoggerConfig(**config)
        except Exception as _:
            return AppLoggerConfig()

    @classmethod
    def _find_files(cls) -> tuple[str, str]:
        current_dir = os.path.abspath(os.path.dirname(__file__))
        base_config_file = os.path.join(os.getcwd(), cls.CONFIG_FILE)

        for _ in range(cls.SEARCH_LEVELS):
            potential_path = os.path.join(current_dir, cls.CONFIG_FILE)
            if os.path.exists(potential_path):
                base_config_file = potential_path
                break
            current_dir = os.path.dirname(current_dir)

        env = os.getenv(cls.ENVIRONMENT_ENV_VAR)
        base_name, extension = os.path.splitext(base_config_file)
        env_config_file = f"{base_name}.{env}{extension}"

        return base_config_file, env_config_file

    @classmethod
    def _merge_configs(cls, base: dict, override: dict) -> dict:
        for key, value in override.items():
            if key in base:
                if isinstance(base[key], dict) and isinstance(value, dict):
                    cls._merge_configs(base[key], value)
                elif isinstance(base[key], list) and isinstance(value, list):
                    base[key] = value
                else:
                    base[key] = value
            else:
                base[key] = value
        return base