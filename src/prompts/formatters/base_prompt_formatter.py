"""Base interface for prompt formatters.

This module defines the interface that all prompt formatters must implement.
Each formatter is responsible for adapting prompts to specific model requirements.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from ...config.base_config import BaseConfig


class PromptFormatError(Exception):
    """Base exception for prompt formatting errors."""
    pass


class ModelFormatError(PromptFormatError):
    """Raised when model-specific formatting fails."""
    pass


class FormatValidationError(PromptFormatError):
    """Raised when formatted prompt validation fails."""
    pass


class BasePromptFormatter(ABC):
    """Base interface for prompt formatters.
    
    Prompt formatters are responsible for:
    1. Adapting prompts to model-specific formats
    2. Validating formatted prompts
    3. Handling model-specific requirements
    4. Managing format-specific resources
    """
    
    @abstractmethod
    def initialize(self, config: BaseConfig) -> None:
        """Initialize the formatter with configuration.
        
        Args:
            config: Formatter configuration
            
        Raises:
            ValueError: If configuration is invalid
            ModelFormatError: If initialization fails
        """
        pass
        
    @abstractmethod
    def format_prompt(
        self,
        prompt: str,
        model_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format a prompt for a specific model type.
        
        Args:
            prompt: The original prompt to format
            model_type: Type of model to format for
            context: Optional additional context for formatting
            
        Returns:
            str: The formatted prompt
            
        Raises:
            ModelFormatError: If formatting fails
            FormatValidationError: If formatted prompt is invalid
        """
        pass
        
    @abstractmethod
    def validate_format(self, formatted_prompt: str, model_type: str) -> bool:
        """Validate that a formatted prompt meets model requirements.
        
        Args:
            formatted_prompt: The formatted prompt to validate
            model_type: Type of model to validate for
            
        Returns:
            bool: True if prompt format is valid
            
        Raises:
            FormatValidationError: If validation fails with specific reason
        """
        pass
        
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up any resources used by the formatter.
        
        This method must be idempotent and safe to call multiple times.
        """
        pass 