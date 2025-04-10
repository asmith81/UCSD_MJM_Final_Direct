"""
Base interface for configuration management.

This module defines the standard interface that all configuration managers must follow.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Union

from .base_config import BaseConfig
from .config_factory import ConfigFactory
from .config_types import ConfigType


class BaseConfigManager(ABC):
    """
    Abstract base class for configuration management.
    
    This class defines the interface that all configuration managers must follow.
    It provides a standard contract for configuration loading and caching.
    
    All implementations must properly handle:
    - Configuration loading and validation
    - Configuration caching (if needed)
    - Type-safe configuration objects
    - Error handling
    """
    
    @abstractmethod
    def __init__(self, config_root: Union[str, Path], config_factory: ConfigFactory):
        """
        Initialize the configuration manager.
        
        Args:
            config_root: Root directory containing configuration files
            config_factory: Factory for creating configuration objects
        """
        pass
    
    @abstractmethod
    def get_config(self, config_type: ConfigType, config_name: str) -> BaseConfig:
        """
        Get a configuration by type and name.
        
        Args:
            config_type: Type of configuration to load
            config_name: Name of the configuration
            
        Returns:
            BaseConfig: The loaded configuration object
            
        Raises:
            ConfigurationError: If configuration cannot be loaded or is invalid
        """
        pass
    
    @abstractmethod
    def invalidate_cache(self, config_type: Optional[ConfigType] = None) -> None:
        """
        Invalidate the configuration cache.
        
        Args:
            config_type: Specific configuration type to invalidate, or None for all
        """
        pass
    
    @abstractmethod
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
        pass 