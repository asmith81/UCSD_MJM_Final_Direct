"""Factory for creating prompt formatters.

This module provides a factory for creating and managing prompt formatters
for different model types.
"""

from typing import Dict, Type, Optional
from pathlib import Path

from ...config.base_config import BaseConfig
from .base_prompt_formatter import BasePromptFormatter, ModelFormatError
from .implementations.basic_formatter import BasicFormatter
from .implementations.llama_formatter import LlamaFormatter
from .implementations.doctr_formatter import DoctrFormatter
from .implementations.pixtral_formatter import PixtralFormatter


class PromptFormatterFactory:
    """Factory for creating prompt formatter instances.
    
    This factory manages:
    1. Registration of formatter implementations
    2. Creation of formatters with configuration
    3. Validation of model type support
    4. Resource cleanup
    """
    
    # Registry of available formatter implementations
    REGISTRY: Dict[str, Type[BasePromptFormatter]] = {}
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize the factory.
        
        Args:
            config_dir: Optional path to formatter configurations
        """
        self.config_dir = config_dir
        self._active_formatters: Dict[str, BasePromptFormatter] = {}
        self._register_default_formatters()
        
    def _register_default_formatters(self) -> None:
        """Register the default formatter implementations."""
        self.register_formatter("basic", BasicFormatter)
        self.register_formatter("llama", LlamaFormatter)
        self.register_formatter("doctr", DoctrFormatter)
        self.register_formatter("pixtral", PixtralFormatter)
        
    def create_formatter(
        self,
        model_type: str,
        config: Optional[BaseConfig] = None
    ) -> BasePromptFormatter:
        """Create a formatter for a specific model type.
        
        Args:
            model_type: Type of model to create formatter for
            config: Optional explicit configuration
            
        Returns:
            BasePromptFormatter: The initialized formatter
            
        Raises:
            ValueError: If model_type is not supported
            ModelFormatError: If formatter creation fails
        """
        if model_type not in self.REGISTRY:
            raise ValueError(f"Unsupported model type: {model_type}")
            
        try:
            # Create formatter instance
            formatter_class = self.REGISTRY[model_type]
            formatter = formatter_class()
            
            # Initialize with configuration
            if config:
                formatter.initialize(config)
                
            # Track for cleanup
            self._active_formatters[model_type] = formatter
            
            return formatter
            
        except Exception as e:
            raise ModelFormatError(f"Failed to create formatter for {model_type}: {e}")
            
    @classmethod
    def register_formatter(
        cls,
        model_type: str,
        formatter_class: Type[BasePromptFormatter]
    ) -> None:
        """Register a new formatter implementation.
        
        Args:
            model_type: Type identifier for the formatter
            formatter_class: Class implementing BasePromptFormatter
            
        Raises:
            ValueError: If model_type is invalid or already registered
            TypeError: If formatter_class doesn't implement BasePromptFormatter
        """
        # Validate formatter class
        if not issubclass(formatter_class, BasePromptFormatter):
            raise TypeError(
                f"Formatter class must implement BasePromptFormatter: {formatter_class}"
            )
            
        # Check for duplicate registration
        if model_type in cls.REGISTRY:
            raise ValueError(f"Formatter already registered for: {model_type}")
            
        cls.REGISTRY[model_type] = formatter_class
        
    def cleanup(self) -> None:
        """Clean up all active formatters.
        
        This method:
        1. Calls cleanup on all active formatters
        2. Clears the active formatters dictionary
        3. Is safe to call multiple times
        """
        for formatter in self._active_formatters.values():
            formatter.cleanup()
        self._active_formatters.clear() 