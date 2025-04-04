"""
Prompt configuration implementation.
"""
from typing import Dict, Any, List, Optional, Union
from ..base_config import BaseConfig


class PromptConfig(BaseConfig):
    """
    Configuration implementation for prompt settings.
    Handles nested configuration structures and validates prompt-specific requirements.
    """

    def __init__(self, data: Dict[str, Any]):
        """
        Initialize with prompt configuration data.
        
        Args:
            data: Raw configuration data
        """
        self.data = data.get('prompt', {})
        if not self.data:
            raise ValueError("Configuration must contain a 'prompt' section")

    def validate(self) -> bool:
        """
        Validate prompt configuration data structure and values.
        
        Returns:
            bool: True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate config info if present
        if 'config_info' in self.data:
            info = self.data['config_info']
            required_info = ['name', 'description', 'version']
            for field in required_info:
                if field not in info:
                    raise ValueError(f"Missing required field in config_info: {field}")
        
        # Validate prompts section
        if 'prompts' not in self.data:
            raise ValueError("Configuration must contain a 'prompts' section")
        
        prompts = self.data['prompts']
        if not isinstance(prompts, list):
            raise ValueError("Prompts must be a list")
        
        # Validate each prompt
        for prompt in prompts:
            required_fields = ['name', 'text', 'category', 'field_to_extract']
            for field in required_fields:
                if field not in prompt:
                    raise ValueError(f"Missing required field in prompt: {field}")
            
            # Validate metadata if present
            if 'metadata' in prompt:
                metadata = prompt['metadata']
                if not isinstance(metadata, dict):
                    raise ValueError("Prompt metadata must be a dictionary")
                if 'source' not in metadata:
                    raise ValueError("Prompt metadata must include a source")
        
        return True

    def get_data(self) -> Dict[str, Any]:
        """
        Get the raw prompt configuration data.
        
        Returns:
            Dict[str, Any]: The prompt configuration data
        """
        return self.data

    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the configuration using dot notation.
        
        Args:
            key: The key to retrieve (e.g., "config_info.version")
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
            section: The section name (e.g., "config_info", "prompts")
            
        Returns:
            Dict[str, Any]: The section data
        """
        return self.data.get(section, {})

    def get_prompts_by_field(self, field: str) -> List[Dict[str, Any]]:
        """
        Get all prompts targeting a specific field.
        
        Args:
            field: The field to extract (e.g., "work_order", "cost")
            
        Returns:
            List[Dict[str, Any]]: List of prompts for the specified field
        """
        prompts = self.data.get('prompts', [])
        return [p for p in prompts if p.get('field_to_extract') == field]

    def get_prompts_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all prompts of a specific category.
        
        Args:
            category: The prompt category (e.g., "detailed")
            
        Returns:
            List[Dict[str, Any]]: List of prompts in the specified category
        """
        prompts = self.data.get('prompts', [])
        return [p for p in prompts if p.get('category') == category] 