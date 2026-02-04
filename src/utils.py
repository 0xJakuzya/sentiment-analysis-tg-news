import json
from pathlib import Path

class AppConfig:

    _instance = None
    _configs = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._load_all_configs()
        return cls._instance
    
    @classmethod
    def _load_all_configs(cls, config_dir="config"):
        config_path = Path(config_dir)
        for config_file in config_path.glob("*.json"):
            with open(config_file, 'r', encoding='utf-8') as f:
                cls._configs[config_file.stem] = json.load(f)
    
    @classmethod
    def get(cls, key, default=None):
        return cls._configs.get(key, default)

config = AppConfig()