"""
Base interface for prompt generators.

This module defines the base interface that all prompt generators must implement.
Each implementation must provide specific prompt generation strategies while
adhering to the common interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from .prompt_config import PromptConfig, PromptTemplate


class BasePromptGenerator(ABC):
    """
    Base interface for prompt generators.
    
    All prompt generators must implement this interface to ensure
    consistent behavior across different prompt generation strategies.
    
    The prompt generator is responsible for:
    1. Managing prompt templates
    2. Validating configurations
    3. Generating prompts based on context
    4. Handling prompt-specific formatting
    5. Managing generator lifecycle
    
    Implementations should:
    - Be thread-safe
    - Handle resource cleanup properly
    - Validate all inputs
    - Provide clear error messages
    - Document any specific requirements
    """
    
    @abstractmethod
    def initialize(self, config: PromptConfig) -> None:
        """
        Initialize the generator with configuration.
        
        This method should:
        1. Validate the configuration
        2. Set up any required resources
        3. Load and validate templates
        4. Initialize internal state
        
        Args:
            config: Configuration for the generator
            
        Raises:
            ValueError: If configuration is invalid
            RuntimeError: If initialization fails
        """
        pass
        
    @abstractmethod
    def generate_prompt(self, context: Dict[str, Any]) -> str:
        """
        Generate a prompt based on context.
        
        This method should:
        1. Validate the context
        2. Select appropriate template(s)
        3. Format the template with context
        4. Apply any generator-specific processing
        
        Args:
            context: Dictionary containing context for prompt generation
                Must include:
                - field_type: Type of field to extract
                - format_instructions: Optional formatting requirements
                - examples: Optional examples to include
                
        Returns:
            str: The generated prompt string
            
        Raises:
            ValueError: If context is invalid or missing required fields
            RuntimeError: If prompt generation fails
        """
        pass
        
    @abstractmethod
    def validate_config(self, config: PromptConfig) -> bool:
        """
        Validate generator configuration.
        
        This method should verify:
        1. All required fields are present
        2. Field values are valid
        3. Templates are well-formed
        4. Generator-specific requirements are met
        
        Args:
            config: Configuration to validate
            
        Returns:
            bool: True if configuration is valid
            
        Raises:
            ValueError: If validation fails with specific reason
        """
        pass
        
    @abstractmethod
    def get_template(self, template_name: str) -> Optional[PromptTemplate]:
        """
        Retrieve a specific template by name.
        
        Args:
            template_name: Name of the template to retrieve
            
        Returns:
            Optional[PromptTemplate]: The template if found, None otherwise
        """
        pass
        
    @abstractmethod
    def get_templates_for_field(self, field_type: str) -> List[PromptTemplate]:
        """
        Get all templates for a specific field type.
        
        Args:
            field_type: Type of field to get templates for
            
        Returns:
            List[PromptTemplate]: List of templates for the field type
        """
        pass
        
    @abstractmethod
    def cleanup(self) -> None:
        """
        Clean up any resources used by the generator.
        
        This method should:
        1. Release any held resources
        2. Clear any caches
        3. Reset internal state
        
        This method must be idempotent and safe to call multiple times.
        """
        pass
