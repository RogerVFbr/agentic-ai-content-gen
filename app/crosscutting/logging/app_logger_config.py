import json
import os
from dotenv import load_dotenv

from pydantic import BaseModel

from enum import Enum

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
    CONFIG_FILE = 'logger_configs.json'

    @classmethod
    def parse(cls) -> AppLoggerConfig:
        try:
            load_dotenv()
            env = os.getenv(cls.ENVIRONMENT_ENV_VAR)
            base_config_file = f'{os.getcwd()}/{cls.CONFIG_FILE}'
            env_config_file = f'{os.getcwd()}/{f".{env}.".join(cls.CONFIG_FILE.split("."))}'

            if not os.path.exists(base_config_file):
                return AppLoggerConfig()

            with open(base_config_file, 'r') as file:
                config = json.load(file)

            if os.path.exists(env_config_file):
                with open(env_config_file, 'r') as file:
                    env_config = json.load(file)
                config = cls._merge_configs(config, env_config)

            return AppLoggerConfig(**config)
        except Exception as e:
            return AppLoggerConfig()

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