"""
Configuration management system.
Handles loading, validation, and caching of configuration files.
"""
from enum import Enum, auto
from pathlib import Path
from typing import Dict, Any, Optional, Union
import yaml

from .base_config import BaseConfig
from .config_factory import ConfigFactory

class ConfigType(Enum):
    """Enumeration of configuration types."""
    MODEL = auto()
    PROMPT = auto()
    EVALUATION = auto()

class ConfigurationError(Exception):
    """Base class for configuration-related errors."""
    pass

class ConfigManager:
    """
    Manages configuration loading and caching.
    Provides a centralized point for configuration management.
    """

    # Configuration directory structure
    CONFIG_PATHS = {
        ConfigType.MODEL: "models",
        ConfigType.PROMPT: "prompts",
        ConfigType.EVALUATION: "evaluation"
    }

    def __init__(self, config_root: Union[str, Path], config_factory: ConfigFactory):
        """
        Initialize the configuration manager.

        Args:
            config_root: Root directory containing configuration files
            config_factory: Factory for creating configuration objects
        """
        self.config_root = Path(config_root)
        self.config_factory = config_factory
        self._config_cache: Dict[str, BaseConfig] = {}

    def get_config(self, config_type: ConfigType, name: Optional[str] = None) -> BaseConfig:
        """
        Get a configuration by type and name.
        Uses caching to avoid reloading unchanged configurations.

        Args:
            config_type: Type of configuration to load
            name: Name of the configuration (optional for single-file configs like evaluation)

        Returns:
            BaseConfig: The loaded configuration object

        Raises:
            ConfigurationError: If configuration cannot be loaded or is invalid
        """
        cache_key = f"{config_type.name}:{name or 'default'}"
        
        # Return cached config if available
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]

        try:
            # Load and cache the configuration
            config = self._load_config(config_type, name)
            self._config_cache[cache_key] = config
            return config
        except Exception as e:
            raise ConfigurationError(f"Failed to load {config_type.name} configuration: {str(e)}")

    def _load_config(self, config_type: ConfigType, name: Optional[str] = None) -> BaseConfig:
        """
        Load a configuration file and create the appropriate config object.

        Args:
            config_type: Type of configuration to load
            name: Name of the configuration file (without extension)

        Returns:
            BaseConfig: The loaded configuration object

        Raises:
            FileNotFoundError: If configuration file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        # Build the configuration file path
        if name:
            file_path = self.config_root / self.CONFIG_PATHS[config_type] / f"{name}.yaml"
        else:
            file_path = self.config_root / f"{self.CONFIG_PATHS[config_type]}.yaml"

        # Ensure the file exists
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        # Load and parse the YAML file
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML file {file_path}: {str(e)}")

        # Create and return the appropriate configuration object
        if config_type == ConfigType.MODEL:
            return self.config_factory.create_model_config(data)
        elif config_type == ConfigType.PROMPT:
            return self.config_factory.create_prompt_config(data)
        elif config_type == ConfigType.EVALUATION:
            return self.config_factory.create_evaluation_config(data)
        else:
            raise ValueError(f"Unsupported configuration type: {config_type}")

    def invalidate_cache(self, config_type: Optional[ConfigType] = None):
        """
        Invalidate the configuration cache.

        Args:
            config_type: Specific configuration type to invalidate, or None for all
        """
        if config_type:
            # Remove specific config type from cache
            self._config_cache = {
                k: v for k, v in self._config_cache.items()
                if not k.startswith(f"{config_type.name}:")
            }
        else:
            # Clear entire cache
            self._config_cache.clear()

    def reload_config(self, config_type: ConfigType, name: Optional[str] = None) -> BaseConfig:
        """
        Force reload a configuration from disk.

        Args:
            config_type: Type of configuration to reload
            name: Name of the configuration to reload

        Returns:
            BaseConfig: The reloaded configuration object
        """
        self.invalidate_cache(config_type)
        return self.get_config(config_type, name) 