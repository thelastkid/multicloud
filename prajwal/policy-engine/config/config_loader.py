"""Policy configuration loader."""
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..utils.logger import get_logger


class ConfigLoader:
    """Load and manage policy configurations."""
    
    def __init__(self):
        self.logger = get_logger("ConfigLoader")
    
    @staticmethod
    def load_yaml(file_path: str) -> Dict[str, Any]:
        """Load YAML configuration file."""
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    
    @staticmethod
    def load_json(file_path: str) -> Dict[str, Any]:
        """Load JSON configuration file."""
        with open(file_path, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def save_yaml(data: Dict[str, Any], file_path: str) -> None:
        """Save configuration to YAML file."""
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
    
    @staticmethod
    def save_json(data: Dict[str, Any], file_path: str) -> None:
        """Save configuration to JSON file."""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
