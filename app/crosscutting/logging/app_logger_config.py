import inspect

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

            # Default path
            base_config_file = f'{os.getcwd()}/{cls.CONFIG_FILE}'
            env_config_file = f'{os.getcwd()}/{f".{env}.".join(cls.CONFIG_FILE.split("."))}'

            # Alternative locations
            alternative_paths = cls._get_alternative_paths(cls.CONFIG_FILE)
            base_config_file = cls._find_file(base_config_file, alternative_paths)
            env_config_file = cls._find_file(env_config_file, alternative_paths)

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
    def _get_alternative_paths(cls, filename: str) -> list[str]:
        # Get the directory of the current file
        current_dir = os.path.dirname(inspect.getfile(cls))
        paths = [current_dir]
        for i in range(1, 4):  # 1 level up to 3 levels up
            paths.append(os.path.abspath(os.path.join(current_dir, *['..'] * i)))
        return [os.path.join(path, filename) for path in paths]

    @classmethod
    def _find_file(cls, default_path: str, alternative_paths: list[str]) -> str:
        # Check default path first
        if os.path.exists(default_path):
            return default_path
        # Check alternative paths
        for path in alternative_paths:
            if os.path.exists(path):
                return path
        return None

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