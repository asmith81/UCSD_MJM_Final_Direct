"""
Configuration management system.
Handles loading, validation, and caching of configuration files.
"""
import os
from typing import Dict, Any, Optional, Union
import logging
import yaml

from .base_config import BaseConfig
from .base_config_manager import BaseConfigManager
from .config_factory import ConfigFactory
from .config_types import ConfigType

# Set up logger for this module
logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Base class for configuration-related errors."""
    pass


class ConfigManager(BaseConfigManager):
    """
    Manages configuration loading and caching.
    Provides a centralized point for configuration management.
    
    This class implements the BaseConfigManager interface, providing:
    - Configuration loading and validation
    - Configuration caching
    - Type-safe configuration objects
    - Proper error handling
    
    Dependencies:
        - config_root: Root directory containing configuration files
        - config_factory: Factory for creating configuration objects
    """

    # Configuration directory structure
    CONFIG_PATHS = {
        ConfigType.MODEL: "models",
        ConfigType.PROMPT: "prompts",
        ConfigType.EVALUATION: "evaluation"
    }

    def __init__(self, config_root: str, config_factory: ConfigFactory):
        """
        Initialize the configuration manager.
        
        Args:
            config_root: Root directory for configuration files
            config_factory: Factory for creating config instances
            
        Raises:
            ValueError: If config_root or config_factory is None
        """
        if not config_root:
            raise ValueError("config_root must be provided")
        if not config_factory:
            raise ValueError("config_factory must be provided")
            
        self._config_root = config_root
        self._config_factory = config_factory
        self._cache: Dict[str, BaseConfig] = {}

    def get_config(self, config_type: ConfigType, config_name: str) -> BaseConfig:
        """
        Get a configuration by type and name.
        Uses caching to avoid reloading unchanged configurations.
        
        Args:
            config_type: Type of configuration to load
            config_name: Name of the configuration
            
        Returns:
            BaseConfig: The loaded configuration object
            
        Raises:
            ConfigurationError: If configuration cannot be loaded or is invalid
        """
        cache_key = f"{config_type.name}:{config_name}"
        
        # Return cached config if available
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            # Load and cache the configuration
            config = self._load_config(config_type, config_name)
            self._cache[cache_key] = config
            return config
        except Exception as e:
            raise ConfigurationError(f"Failed to load {config_type.name} configuration: {str(e)}")

    def invalidate_cache(self, config_type: Optional[ConfigType] = None) -> None:
        """
        Invalidate the configuration cache.
        
        Args:
            config_type: Specific configuration type to invalidate, or None for all
        """
        if config_type is None:
            self._cache.clear()
        else:
            keys = [k for k in self._cache if k.startswith(config_type.name)]
            for k in keys:
                del self._cache[k]

    def reload_config(self, config_type: ConfigType, config_name: str) -> BaseConfig:
        """
        Force reload a configuration from disk.
        
        Args:
            config_type: Type of configuration to reload
            config_name: Name of the configuration to reload
            
        Returns:
            BaseConfig: The reloaded configuration object
            
        Raises:
            ConfigurationError: If configuration cannot be loaded or is invalid
        """
        cache_key = f"{config_type.name}:{config_name}"
        if cache_key in self._cache:
            del self._cache[cache_key]
        return self.get_config(config_type, config_name)

    def _load_config(self, config_type: ConfigType, config_name: str) -> BaseConfig:
        """
        Load a configuration file and create the appropriate config object.
        
        Args:
            config_type: Type of configuration to load
            config_name: Name of the configuration file (without extension)
            
        Returns:
            BaseConfig: The loaded configuration object
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            yaml.YAMLError: If YAML parsing fails
            ConfigurationError: If configuration is invalid
        """
        # Build the configuration file path
        config_path = os.path.join(self._config_root, self.CONFIG_PATHS[config_type], f"{config_name}.yaml")

        # Ensure the file exists
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        # Load and parse the YAML file
        try:
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML file {config_path}: {str(e)}")

        # Create and return the appropriate configuration object
        try:
            return self._config_factory.create_config(config_type, data)
        except Exception as e:
            raise ConfigurationError(f"Failed to create configuration object: {str(e)}") 