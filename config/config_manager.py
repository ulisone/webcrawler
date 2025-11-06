import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigManager:
    _instance: Optional['ConfigManager'] = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls) -> 'ConfigManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._config_file = None
            self._initialized = True
    
    def load_config(self, config_file: str = None) -> Dict[str, Any]:
        if config_file is None:
            config_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                'config', 'config.yaml'
            )
        
        self._config_file = config_file
        
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file not found: {config_file}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                self._config = yaml.safe_load(file)
            return self._config
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_crawler_config(self) -> Dict[str, Any]:
        return self.get('crawler', {})
    
    def get_ftp_config(self) -> Dict[str, Any]:
        return self.get('ftp', {})
    
    def get_api_config(self) -> Dict[str, Any]:
        return self.get('api', {})


    def update_config(self, key: str, value: Any) -> None:
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_config(self, config_file: str = None) -> None:
        if config_file is None:
            config_file = self._config_file
        
        if config_file is None:
            raise ValueError("No config file specified")
        
        try:
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as file:
                yaml.safe_dump(self._config, file, default_flow_style=False, 
                             ensure_ascii=False, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to save config: {e}")
    
    def validate_config(self) -> bool:
        required_sections = ['crawler', 'ftp', 'api']
        for section in required_sections:
            if section not in self._config:
                raise ValueError(f"Missing required config section: {section}")
        
        monitoring = self.get_monitoring_config()
        if not monitoring.get('watch_directory'):
            raise ValueError("Missing required config: monitoring.watch_directory")
        
        ftp = self.get_ftp_config()
        if not ftp.get('host'):
            raise ValueError("Missing required config: ftp.host")
        
        api = self.get_api_config()
        if not api.get('base_url'):
            raise ValueError("Missing required config: api.base_url")
        
        return True