"""
Model configuration implementation.
"""
from typing import Dict, Any, Optional, Union
from ..base_config import BaseConfig


class ModelConfig(BaseConfig):
    """
    Configuration implementation for model settings.
    Handles nested configuration structures and validates model-specific requirements.
    """

    def __init__(self, data: Dict[str, Any]):
        """
        Initialize with model configuration data.
        
        Args:
            data: Raw configuration data
        """
        self.data = data.get('model', {})
        if not self.data:
            raise ValueError("Configuration must contain a 'model' section")

    def validate(self) -> bool:
        """
        Validate model configuration data structure and values.
        
        Returns:
            bool: True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate required top-level fields
        required_fields = ['name', 'type', 'parameters']
        for field in required_fields:
            if field not in self.data:
                raise ValueError(f"Missing required field in model section: {field}")
        
        # Validate hardware requirements if present
        if 'hardware' in self.data:
            hardware = self.data['hardware']
            if 'gpu_required' in hardware and hardware['gpu_required']:
                if 'gpu_memory_min' not in hardware:
                    raise ValueError("GPU memory requirement must be specified when GPU is required")
        
        # Validate inference parameters if present
        if 'inference' in self.data:
            inference = self.data['inference']
            if 'temperature' in inference:
                temp = inference['temperature']
                if not isinstance(temp, (int, float)) or temp < 0:
                    raise ValueError("Temperature must be a non-negative number")
        
        return True

    def get_data(self) -> Dict[str, Any]:
        """
        Get the raw model configuration data.
        
        Returns:
            Dict[str, Any]: The model configuration data
        """
        return self.data

    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the configuration using dot notation.
        
        Args:
            key: The key to retrieve (e.g., "hardware.gpu_memory_min")
            default: Default value if key is not found
            
        Returns:
            Any: The value at the specified key path
        """
        current = self.data
        for part in key.split('.'):
            if not isinstance(current, dict):
                return default
            current = current.get(part, default)
            if current is default:
                return default
        return current

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire section of the configuration.
        
        Args:
            section: The section name (e.g., "hardware", "inference")
            
        Returns:
            Dict[str, Any]: The section data
        """
        return self.data.get(section, {}) 