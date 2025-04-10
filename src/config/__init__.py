"""
Configuration system initialization.

This module provides access to configuration management components.
Note: As of v2.0, the global configuration manager has been removed to enforce
proper dependency injection. Configuration managers must now be explicitly created
and passed to components that need them.
"""
from .base_config import BaseConfig
from .base_config_manager import BaseConfigManager
from .config_factory import ConfigFactory
from .config_manager import ConfigManager, ConfigurationError
from .config_types import ConfigType

__all__ = [
    # Base interfaces
    'BaseConfig',
    'BaseConfigManager',
    
    # Implementation
    'ConfigManager',
    'ConfigFactory',
    
    # Types and errors
    'ConfigType',
    'ConfigurationError',
]
