"""Pixtral-specific prompt formatter implementation.

This module provides a formatter specifically designed for Pixtral model prompts,
following the Mistral chat format requirements.

References:
- Model: https://huggingface.co/mistral-community/pixtral-12b
- Format: Based on Mistral chat format
"""

from typing import Dict, Any, Optional

from ..base_prompt_formatter import (
    BasePromptFormatter,
    ModelFormatError,
    FormatValidationError
)
from ...config.base_config import BaseConfig


class PixtralFormatter(BasePromptFormatter):
    """Formatter for Pixtral model prompts.
    
    This formatter implements Pixtral-specific formatting:
    1. System/user message structure (Mistral format)
    2. Length validation
    3. Required section validation
    4. Format-specific validation
    
    Format structure:
    {system}\n\nUser: {prompt}\nAssistant:
    """
    
    def __init__(self):
        """Initialize the Pixtral formatter."""
        self._config = None
        self._format_template = None
        self._system_message = None
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
            format_config = config.formats.get("pixtral", {})
            
            # Get format template and system message
            self._format_template = format_config.get("format_template")
            self._system_message = format_config.get("system_message")
            
            if not self._format_template or not self._system_message:
                raise ValueError("Format template or system message not found")
                
            # Get validation rules
            self._validation_rules = format_config.get("validation", {})
            self._max_length = format_config.get("max_length")
            
        except Exception as e:
            raise ModelFormatError(f"Failed to initialize Pixtral formatter: {e}")
            
    def format_prompt(
        self,
        prompt: str,
        model_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format a prompt for the Pixtral model.
        
        Args:
            prompt: The original prompt to format
            model_type: Must be "pixtral"
            context: Optional additional context
            
        Returns:
            str: The formatted prompt
            
        Raises:
            ModelFormatError: If formatting fails
            FormatValidationError: If formatted prompt is invalid
        """
        if not self._config:
            raise ModelFormatError("Formatter not initialized")
            
        if model_type != "pixtral":
            raise ModelFormatError(f"Unsupported model type: {model_type}")
            
        try:
            # Format the prompt with template
            formatted = self._format_template.format(
                system=self._system_message,
                prompt=prompt
            )
            
            # Validate the formatted prompt
            if not self.validate_format(formatted, model_type):
                raise FormatValidationError("Generated prompt failed validation")
                
            return formatted
            
        except KeyError as e:
            raise ModelFormatError(f"Missing required prompt field: {e}")
        except Exception as e:
            raise ModelFormatError(f"Failed to format prompt: {e}")
            
    def validate_format(self, formatted_prompt: str, model_type: str) -> bool:
        """Validate that a formatted prompt meets Pixtral requirements.
        
        Args:
            formatted_prompt: The formatted prompt to validate
            model_type: Must be "pixtral"
            
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
                
        # Check Pixtral-specific format requirements
        if "User:" not in formatted_prompt:
            raise FormatValidationError("Missing User: marker")
        if "Assistant:" not in formatted_prompt:
            raise FormatValidationError("Missing Assistant: marker")
            
        return True
        
    def cleanup(self) -> None:
        """Clean up any resources.
        
        This implementation has no resources to clean up.
        """
        pass 