"""
Configuration system initialization.
Provides centralized access to configuration management.
"""
from pathlib import Path
from typing import Optional

from .config_manager import ConfigManager, ConfigType
from .config_factory import ConfigFactory

# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None

def init_config(config_root: str | Path) -> ConfigManager:
    """
    Initialize the configuration management system.
    
    Args:
        config_root: Root directory containing configuration files
        
    Returns:
        ConfigManager: The initialized configuration manager
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(
            config_root=config_root,
            config_factory=ConfigFactory()
        )
    return _config_manager

def get_config_manager() -> ConfigManager:
    """
    Get the global configuration manager instance.
    
    Returns:
        ConfigManager: The configuration manager instance
        
    Raises:
        RuntimeError: If configuration system is not initialized
    """
    if _config_manager is None:
        raise RuntimeError(
            "Configuration system not initialized. Call init_config first."
        )
    return _config_manager

# Export ConfigType for convenience
__all__ = ['init_config', 'get_config_manager', 'ConfigType']
