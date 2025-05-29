from pathlib import Path

import json
import os

from configurations.configs import Configs


class ConfigsParser:

    def parse(self) -> Configs:
        env = os.getenv('APP_ENV')

        project_root = Path(__file__).parent.parent  # Adjust based on your file structure
        base_config_file = project_root / 'configs.json'
        env_config_file = project_root / f'configs.{env}.json'

        if not os.path.exists(base_config_file):
            raise FileNotFoundError(f"Configuration file '{base_config_file}'")

        if not os.path.exists(env_config_file):
            raise FileNotFoundError(f"Configuration file '{env_config_file}'")

        with open(base_config_file, 'r') as file:
            config = json.load(file)

        if os.path.exists(env_config_file):
            with open(env_config_file, 'r') as file:
                env_config = json.load(file)
            config = self._merge_configs(config, env_config)

        return Configs(**config)

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