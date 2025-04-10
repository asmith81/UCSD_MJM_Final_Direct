"""Configuration for prompt formatters.

This module provides configuration management for prompt formatters,
handling format templates and validation rules.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ...config.base_config import BaseConfig


@dataclass
class FormatValidationRules:
    """Validation rules for a prompt format.
    
    Attributes:
        required_sections: Sections that must be present
        max_tokens: Maximum allowed tokens
        min_prompt_length: Minimum prompt length
        max_prompt_length: Maximum prompt length
    """
    required_sections: List[str]
    max_tokens: int
    min_prompt_length: Optional[int] = None
    max_prompt_length: Optional[int] = None


@dataclass
class ModelFormatConfig:
    """Configuration for a specific model's format.
    
    Attributes:
        max_length: Maximum length for this format
        format_template: Template string for formatting
        system_message: Optional system message
        validation: Validation rules
    """
    max_length: int
    format_template: str
    system_message: Optional[str]
    validation: FormatValidationRules


class PromptFormatConfig(BaseConfig):
    """Configuration for prompt formats.
    
    This class manages:
    1. Format templates for different models
    2. Validation rules
    3. Default configurations
    4. Format-specific settings
    """
    
    def __init__(
        self,
        formats: Dict[str, Dict[str, Any]],
        default_format: str,
        validation: Dict[str, Any]
    ):
        """Initialize format configuration.
        
        Args:
            formats: Format configurations by model type
            default_format: Default format to use
            validation: Global validation rules
        """
        self.formats = {}
        self.default_format = default_format
        self.validation = validation
        
        # Process format configurations
        for model_type, format_config in formats.items():
            validation_rules = FormatValidationRules(
                required_sections=format_config["validation"]["required_sections"],
                max_tokens=format_config["validation"]["max_tokens"]
            )
            
            self.formats[model_type] = ModelFormatConfig(
                max_length=format_config["max_length"],
                format_template=format_config["format_template"],
                system_message=format_config.get("system_message"),
                validation=validation_rules
            )
            
    def get_format_config(self, model_type: str) -> ModelFormatConfig:
        """Get format configuration for a model type.
        
        Args:
            model_type: Type of model to get config for
            
        Returns:
            ModelFormatConfig for the specified type
            
        Raises:
            KeyError: If model type not found
        """
        if model_type not in self.formats:
            if self.default_format in self.formats:
                return self.formats[self.default_format]
            raise KeyError(f"No format config for: {model_type}")
        return self.formats[model_type]
        
    def get_data(self) -> Dict[str, Any]:
        """Get the full configuration data.
        
        Returns:
            Dict containing all configuration data
        """
        return {
            "formats": {
                model_type: {
                    "max_length": config.max_length,
                    "format_template": config.format_template,
                    "system_message": config.system_message,
                    "validation": {
                        "required_sections": config.validation.required_sections,
                        "max_tokens": config.validation.max_tokens
                    }
                }
                for model_type, config in self.formats.items()
            },
            "default_format": self.default_format,
            "validation": self.validation
        } 