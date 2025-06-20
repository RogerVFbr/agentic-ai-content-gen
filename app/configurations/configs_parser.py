import json
import os
from string import Template
from typing import Dict, Any


class ConfigsParser:

    SEARCH_LEVELS = 10

    def parse(self, config_file: str , environment_env_var: str = "APP_ENV", require_env_override: bool = False, placeholders: Dict[str, Any] = None) -> dict:
        base_config_file, env_config_file = self._find_files(config_file, environment_env_var)

        if os.path.exists(base_config_file):
            with open(base_config_file, 'r') as file:
                config = file.read()

            if placeholders:
                config = Template(config).substitute(**placeholders)

            config = json.loads(config)
        else:
            raise FileNotFoundError(f"Configuration file '{base_config_file}' not found.")

        if os.path.exists(env_config_file):
            with open(env_config_file, 'r') as file:
                env_config = file.read()

            if placeholders:
                env_config = Template(config).substitute(**placeholders)

            env_config = json.loads(env_config)
            config = self._merge_configs(config, env_config)
        elif require_env_override:
            raise FileNotFoundError(f"Environment configuration file '{env_config_file}' not found.")

        return config

    def _find_files(self, config_file: str, environment_env_var: str) -> tuple[str, str]:
        current_dir = os.path.abspath(os.path.dirname(__file__))
        base_config_file = os.path.join(os.getcwd(), config_file)

        for _ in range(self.SEARCH_LEVELS):
            potential_path = os.path.join(current_dir, config_file)
            if os.path.exists(potential_path):
                base_config_file = potential_path
                break
            current_dir = os.path.dirname(current_dir)

        env = os.getenv(environment_env_var)
        base_name, extension = os.path.splitext(base_config_file)
        env_config_file = f"{base_name}.{env}{extension}"

        return base_config_file, env_config_file

    def _merge_configs(self, base: dict, override: dict) -> dict:
        for key, value in override.items():
            if key in base:
                if isinstance(base[key], dict) and isinstance(value, dict):
                    self._merge_configs(base[key], value)
                elif isinstance(base[key], list) and isinstance(value, list):
                    base[key] = value
                else:
                    base[key] = value
            else:
                base[key] = value
        return base