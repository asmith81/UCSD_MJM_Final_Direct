"""Doctr prompt formatter implementation.

This module provides a formatter specifically designed for Doctr model prompts,
which use a simpler format without system messages.
"""

from typing import Dict, Any, Optional

from ..base_prompt_formatter import (
    BasePromptFormatter,
    ModelFormatError,
    FormatValidationError
)
from ...config.base_config import BaseConfig


class DoctrFormatter(BasePromptFormatter):
    """Formatter for Doctr model prompts.
    
    This formatter implements Doctr-specific formatting:
    1. Simple prompt structure
    2. Length validation
    3. Required section validation
    """
    
    def __init__(self):
        """Initialize the Doctr formatter."""
        self._config = None
        self._format_template = None
        self._validation_rules = None
        self._max_length = None
        
    def initialize(self, config: BaseConfig) -> None:
        """Initialize with configuration.
        
        Args:
            config: Formatter configuration
            
        Raises:
            ValueError: If configuration is invalid
            ModelFormatError: If initialization fails
        """
        try:
            self._config = config
            format_config = config.formats.get("doctr", {})
            
            # Get format template
            self._format_template = format_config.get("format_template")
            if not self._format_template:
                raise ValueError("Format template not found in configuration")
                
            # Get validation rules
            self._validation_rules = format_config.get("validation", {})
            self._max_length = format_config.get("max_length")
            
        except Exception as e:
            raise ModelFormatError(f"Failed to initialize formatter: {e}")
            
    def format_prompt(
        self,
        prompt: str,
        model_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format a prompt for the Doctr model.
        
        Args:
            prompt: The original prompt to format
            model_type: Must be "doctr"
            context: Optional additional context
            
        Returns:
            str: The formatted prompt
            
        Raises:
            ModelFormatError: If formatting fails
            FormatValidationError: If formatted prompt is invalid
        """
        if not self._config:
            raise ModelFormatError("Formatter not initialized")
            
        if model_type != "doctr":
            raise ModelFormatError(f"Unsupported model type: {model_type}")
            
        try:
            # Format the prompt with template
            formatted = self._format_template.format(prompt=prompt)
            
            # Validate the formatted prompt
            if not self.validate_format(formatted, model_type):
                raise FormatValidationError("Generated prompt failed validation")
                
            return formatted
            
        except KeyError as e:
            raise ModelFormatError(f"Missing required prompt field: {e}")
        except Exception as e:
            raise ModelFormatError(f"Failed to format prompt: {e}")
            
    def validate_format(self, formatted_prompt: str, model_type: str) -> bool:
        """Validate that a formatted prompt meets Doctr requirements.
        
        Args:
            formatted_prompt: The formatted prompt to validate
            model_type: Must be "doctr"
            
        Returns:
            bool: True if prompt format is valid
            
        Raises:
            FormatValidationError: If validation fails with specific reason
        """
        if not formatted_prompt:
            raise FormatValidationError("Formatted prompt is empty")
            
        # Check length constraints
        if self._max_length and len(formatted_prompt) > self._max_length:
            raise FormatValidationError(
                f"Prompt exceeds maximum length: {len(formatted_prompt)} > {self._max_length}"
            )
            
        # Check required sections
        required_sections = self._validation_rules.get("required_sections", [])
        for section in required_sections:
            if section not in formatted_prompt:
                raise FormatValidationError(f"Missing required section: {section}")
                
        return True
        
    def cleanup(self) -> None:
        """Clean up any resources.
        
        This implementation has no resources to clean up.
        """
        pass 