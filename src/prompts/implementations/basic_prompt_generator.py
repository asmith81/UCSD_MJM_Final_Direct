"""Basic prompt generator implementation.

This module provides a simple prompt generator that uses direct,
straightforward prompts for field extraction.
"""

from typing import Dict, Any, Optional, List
from ..base_prompt_generator import BasePromptGenerator
from ..prompt_config import PromptConfig, PromptTemplate


class BasicPromptGenerator(BasePromptGenerator):
    """Basic prompt generator implementation.
    
    This generator uses simple, direct prompts for field extraction.
    It focuses on clear, unambiguous instructions without additional
    context or positioning information.
    
    The generator maintains a simple state:
    - Configuration with prompt templates
    - Current active prompt template
    - Field-specific format instructions
    """
    
    def __init__(self):
        """Initialize the basic prompt generator."""
        self._config = None
        self._templates = {}  # Cache for quick template lookup
        self._current_prompt = None
        
    def initialize(self, config: PromptConfig) -> None:
        """Initialize with configuration.
        
        This implementation:
        1. Validates the configuration
        2. Caches templates for quick access
        3. Sets up initial state
        
        Args:
            config: Prompt configuration
            
        Raises:
            ValueError: If configuration is invalid
            RuntimeError: If initialization fails
        """
        if not self.validate_config(config):
            raise ValueError("Invalid configuration provided")
            
        self._config = config
        
        # Cache templates by name and field type for quick access
        self._templates = {
            'by_name': {p.name: p for p in config.prompts},
            'by_field': {}
        }
        
        # Group templates by field type
        for prompt in config.prompts:
            field_prompts = self._templates['by_field'].setdefault(
                prompt.field_to_extract, []
            )
            field_prompts.append(prompt)
            
    def validate_config(self, config: PromptConfig) -> bool:
        """Validate generator configuration.
        
        Verifies:
        1. Config is proper type
        2. Required prompts exist
        3. Templates are well-formed
        
        Args:
            config: Configuration to validate
            
        Returns:
            bool: True if configuration is valid
            
        Raises:
            ValueError: If validation fails with specific reason
        """
        if not isinstance(config, PromptConfig):
            raise ValueError("Config must be instance of PromptConfig")
            
        if not config.prompts:
            raise ValueError("Configuration must include at least one prompt")
            
        # Verify each prompt has required fields
        for prompt in config.prompts:
            if not prompt.name or not prompt.text:
                raise ValueError("Prompts must have name and text")
            if not prompt.field_to_extract:
                raise ValueError("Prompts must specify field_to_extract")
                
        return True
        
    def generate_prompt(self, context: Dict[str, Any]) -> str:
        """Generate a prompt based on context.
        
        This implementation:
        1. Validates the context
        2. Selects appropriate template
        3. Applies field-specific formatting
        
        Args:
            context: Dictionary containing:
                - field_type: Type of field to extract
                - format_instructions: Optional formatting requirements
                - examples: Optional examples to include
                
        Returns:
            str: The generated prompt string
            
        Raises:
            ValueError: If context is invalid or missing required fields
            RuntimeError: If prompt generation fails
        """
        if not self._config:
            raise RuntimeError("Generator not initialized")
            
        field_type = context.get('field_type')
        if not field_type:
            raise ValueError("Context must include field_type")
            
        # Get all prompts for this field type
        prompts = self.get_templates_for_field(field_type)
        if not prompts:
            raise ValueError(f"No prompts found for field type: {field_type}")
            
        # For basic generator, just use the first appropriate prompt
        self._current_prompt = prompts[0]
        
        # Add field-specific format instructions from context or defaults
        format_instructions = context.get('format_instructions', '')
        if not format_instructions:
            if field_type == 'work_order':
                format_instructions = (
                    " The work order number should be exactly 5 alphanumeric "
                    "characters. Preserve any leading zeros."
                )
            elif field_type == 'cost':
                format_instructions = (
                    " Return the amount as a decimal number with exactly 2 decimal "
                    "places. Do not include currency symbols or separators."
                )
                
        # Add examples if provided
        examples = context.get('examples', [])
        examples_text = ""
        if examples:
            examples_text = "\n\nExamples:\n" + "\n".join(examples)
            
        # Combine template with instructions and examples
        prompt = (
            self._current_prompt.text +
            format_instructions +
            examples_text
        )
        
        return prompt
        
    def get_template(self, template_name: str) -> Optional[PromptTemplate]:
        """Retrieve a specific template by name.
        
        Args:
            template_name: Name of the template to retrieve
            
        Returns:
            Optional[PromptTemplate]: The template if found, None otherwise
        """
        return self._templates.get('by_name', {}).get(template_name)
        
    def get_templates_for_field(self, field_type: str) -> List[PromptTemplate]:
        """Get all templates for a specific field type.
        
        Args:
            field_type: Type of field to get templates for
            
        Returns:
            List[PromptTemplate]: List of templates for the field type
        """
        return self._templates.get('by_field', {}).get(field_type, [])
        
    def cleanup(self) -> None:
        """Clean up any resources used by the generator.
        
        This implementation:
        1. Clears template cache
        2. Resets internal state
        """
        self._config = None
        self._templates = {}
        self._current_prompt = None 