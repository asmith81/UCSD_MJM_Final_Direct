"""
Basic prompt generator that uses simple string formatting.
"""
from typing import Any, Dict

from src.prompts.base_prompt_generator import BasePromptGenerator


class BasicPromptGenerator(BasePromptGenerator):
    """
    A basic prompt generator that uses simple string formatting with provided data.
    """
    
    def __init__(self, config, field: str):
        """
        Initialize the basic prompt generator.
        
        Args:
            config: Configuration containing prompt templates
            field: The specific field/key in config that contains this prompt's template
        """
        self.config = config
        self.field = field
        self.template = self.config.get(field)
        
        if not self.template:
            raise ValueError(f"Template for field '{field}' not found in configuration")
    
    def generate_prompt(self, data: Dict[str, Any]) -> str:
        """
        Generate a prompt by formatting the template with the provided data.
        
        Args:
            data: Dictionary containing values to be inserted into the template
            
        Returns:
            str: The formatted prompt
        """
        try:
            return self.template.format(**data)
        except KeyError as e:
            raise ValueError(f"Missing required data field: {e}")
        except Exception as e:
            raise ValueError(f"Error generating prompt: {e}")
