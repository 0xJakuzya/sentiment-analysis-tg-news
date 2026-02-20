import json
from pathlib import Path

# путь к корню проекта (родитель каталога src)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class AppConfig:

    instance = None
    configs = {}

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.load_all_configs()
        return cls.instance

    @classmethod
    def load_all_configs(cls, config_dir="config"):
        config_path = PROJECT_ROOT / config_dir
        for config_file in config_path.glob("*.json"):
            with open(config_file, "r", encoding="utf-8") as f:
                cls.configs[config_file.stem] = json.load(f)

    @classmethod
    def get(cls, key, default=None):
        return cls.configs.get(key, default)


config = AppConfig()