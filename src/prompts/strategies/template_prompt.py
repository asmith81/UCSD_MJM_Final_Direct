"""
Template-based prompt generator that uses Jinja2 templates.
"""
from typing import Any, Dict
import jinja2

from src.prompts.base_prompt_generator import BasePromptGenerator


class TemplatePromptGenerator(BasePromptGenerator):
    """
    A prompt generator that uses Jinja2 templating for more complex prompt formatting.
    Allows for advanced templating features like loops, conditionals, and filters.
    """
    
    def __init__(self, config, field: str):
        """
        Initialize the template prompt generator.
        
        Args:
            config: Configuration containing prompt templates
            field: The specific field/key in config that contains the template
        """
        self.config = config
        self.field = field
        self.template_str = self.config.get(field)
        
        if not self.template_str:
            raise ValueError(f"Template for field '{field}' not found in config")
        
        # Initialize the Jinja2 environment
        self.env = jinja2.Environment(
            loader=jinja2.BaseLoader,
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False
        )
        
        # Compile the template
        try:
            self.template = self.env.from_string(self.template_str)
        except jinja2.exceptions.TemplateSyntaxError as e:
            raise ValueError(f"Invalid template syntax in field '{field}': {e}")
    
    def generate_prompt(self, data: Dict[str, Any]) -> str:
        """
        Generate a prompt by rendering the Jinja2 template with provided data.
        
        Args:
            data: Dictionary containing values to be rendered in the template
            
        Returns:
            str: The rendered prompt
        """
        try:
            return self.template.render(**data)
        except jinja2.exceptions.UndefinedError as e:
            raise ValueError(f"Missing data for template rendering: {e}")
        except Exception as e:
            raise ValueError(f"Error rendering template: {e}") 