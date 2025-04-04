"""
Base configuration interface defining the contract for all configuration types.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union, List


class BaseConfig(ABC):
    """
    Abstract base class for configuration types.
    Defines the interface that all configuration implementations must follow.
    """

    @abstractmethod
    def validate(self) -> bool:
        """
        Validate the configuration data structure and values.
        
        Returns:
            bool: True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        pass

    @abstractmethod
    def get_data(self) -> Dict[str, Any]:
        """
        Get the raw configuration data.
        
        Returns:
            Dict[str, Any]: The configuration data
        """
        pass

    @abstractmethod
    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the configuration using dot notation.
        Example: "hardware.gpu_memory_min"
        
        Args:
            key: The key to retrieve, using dot notation for nested values
            default: Default value if key is not found
            
        Returns:
            Any: The value at the specified key path
        """
        pass

    @abstractmethod
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire section of the configuration.
        
        Args:
            section: The section name (e.g., "hardware", "inference")
            
        Returns:
            Dict[str, Any]: The section data
        """
        pass 