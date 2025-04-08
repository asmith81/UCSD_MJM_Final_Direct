"""
Identity prompt generator that returns the data field directly.
"""
from typing import Any, Dict

from src.prompts.base_prompt_generator import BasePromptGenerator


class IdentityPromptGenerator(BasePromptGenerator):
    """
    A simple prompt generator that returns a specified field from the input data.
    This generator does not apply any transformation to the data.
    """
    
    def __init__(self, config, field: str):
        """
        Initialize the identity prompt generator.
        
        Args:
            config: Configuration (not used in this generator)
            field: The specific field in the input data to return as prompt
        """
        self.field = field
    
    def generate_prompt(self, data: Dict[str, Any]) -> str:
        """
        Generate a prompt by returning the specified field from the input data.
        
        Args:
            data: Dictionary containing the field to be returned
            
        Returns:
            str: The value of the specified field or empty string if field is not found
        """
        if self.field not in data:
            return ""
        
        value = data.get(self.field)
        
        # Handle non-string values
        if not isinstance(value, str):
            try:
                value = str(value)
            except Exception:
                return ""
        
        return value 