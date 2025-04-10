"""
Factory for creating model instances.

This module provides a factory for creating and initializing model instances
based on configuration. It handles dependency injection, configuration validation,
and proper error handling.
"""
from typing import Dict, Type, Any, Optional, Union
from pathlib import Path
import logging

from .base_model import BaseModel
from .error_recovery import ErrorRecoveryManager, with_error_recovery
from .model_errors import (
    ModelError,
    ModelInitializationError,
    ModelConfigError,
    ModelResourceError,
    ModelCreationError,
    ModelLoaderTimeoutError
)
from .retry_utils import RetryConfig, with_retry
from ..config.base_config import BaseConfig
from ..config import get_config_manager, ConfigType, ConfigManager
from ..config.implementations.model_config import ModelConfig

# Set up logger for this module
logger = logging.getLogger(__name__)

class ModelFactory:
    """Factory class for creating model instances.
    
    This class follows dependency injection principles:
    1. Dependencies are injected through constructor
    2. Registry is instance-level, not static
    3. Clear interface dependencies
    """

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """Initialize the model factory.
        
        Args:
            config_manager: Optional configuration manager instance
        """
        self._registry: Dict[str, Type[BaseModel]] = {}
        self._config_manager = config_manager

    @property
    def config_manager(self) -> Optional[ConfigManager]:
        """Get the config manager instance."""
        return self._config_manager

    @config_manager.setter
    def config_manager(self, manager: ConfigManager):
        """Set the config manager instance.
        
        Note: This setter is provided for backward compatibility.
        Prefer passing config_manager through constructor.
        """
        if not isinstance(manager, ConfigManager):
            raise ModelConfigError(
                "Invalid config manager",
                value=type(manager).__name__,
                expected="ConfigManager instance"
            )
        self._config_manager = manager

    def register_model(self, name: str, model_class: Type[BaseModel]) -> None:
        """Register a model class with the factory.

        Args:
            name: The name to register the model under
            model_class: The model class to register
            
        Raises:
            ModelConfigError: If name is empty or model_class is invalid
        """
        if not name:
            raise ModelConfigError("Model name cannot be empty")
            
        if not isinstance(model_class, type) or not issubclass(model_class, BaseModel):
            raise ModelConfigError(
                "Invalid model class",
                value=model_class.__name__ if isinstance(model_class, type) else type(model_class).__name__,
                expected="class inheriting from BaseModel",
                model_name=name
            )
            
        self._registry[name] = model_class

    def create_model(
        self,
        model_type: str,
        config: Optional[Union[Dict[str, Any], ModelConfig]] = None
    ) -> BaseModel:
        """Create a model instance.

        Args:
            model_type: The type of model to create
            config: Model configuration

        Returns:
            The created model instance
            
        Raises:
            ModelConfigError: If model creation fails
        """
        # Load config if not provided
        if config is None:
            if self._config_manager is None:
                raise ModelConfigError(
                    "No configuration provided and no config manager set"
                )
            config = self._config_manager.load_config(model_type)
            
        # Validate config type
        if not isinstance(config, (dict, ModelConfig)):
            raise ModelConfigError(
                "Invalid configuration type",
                value=type(config).__name__,
                expected="dict or ModelConfig"
            )
            
        # Convert dict to ModelConfig if needed
        if isinstance(config, dict):
            config = ModelConfig(config)
            
        # Get model class from registry
        if model_type not in self._registry:
            raise ModelConfigError(
                "Unknown model type",
                value=model_type,
                expected=f"one of {list(self._registry.keys())}"
            )
            
        model_class = self._registry[model_type]
        
        try:
            return model_class(config)
        except Exception as e:
            raise ModelConfigError(
                "Failed to create model instance",
                model_name=model_type,
                parent_error=e
            ) from e

    def _validate_config(self, config: Dict[str, Any], model_type: str) -> None:
        """
        Validate model configuration.
        
        Args:
            config: Configuration dictionary to validate
            model_type: Type of model being configured
            
        Raises:
            ModelConfigError: If configuration is invalid
        """
        if not isinstance(config, dict):
            raise ModelConfigError(
                "Configuration must be a dictionary",
                model_name=model_type,
                parameter="config",
                value=type(config).__name__,
                expected="dict"
            )
            
        # Validate model name if present
        if "model_name" in config:
            model_name = config.get("model_name")
            if not model_name or not isinstance(model_name, str):
                raise ModelConfigError(
                    "Model name must be a non-empty string",
                    model_name=model_type,
                    parameter="model_name",
                    value=model_name
                )
                
        # Validate required parameters are present and have correct types
        model_class = self._registry[model_type]
        required_params = getattr(model_class, "REQUIRED_CONFIG_PARAMS", {})
        
        for param, param_type in required_params.items():
            if param not in config:
                raise ModelConfigError(
                    f"Missing required parameter",
                    model_name=model_type,
                    parameter=param,
                    expected=param_type.__name__
                )
            
            value = config[param]
            if not isinstance(value, param_type):
                raise ModelConfigError(
                    f"Invalid parameter type",
                    model_name=model_type,
                    parameter=param,
                    value=type(value).__name__,
                    expected=param_type.__name__
                )

    def _load_model_config(self, model_name: str) -> ModelConfig:
        """
        Load model configuration from config manager.

        Args:
            model_name: Name of the model configuration to load

        Returns:
            ModelConfig: The loaded configuration

        Raises:
            ModelConfigError: If configuration cannot be loaded or is invalid
        """
        try:
            config = self._config_manager.get_config(ConfigType.MODEL, model_name)
            if not isinstance(config, ModelConfig):
                actual_type = type(config).__name__
                raise ModelConfigError(
                    f"Invalid configuration type",
                    model_name=model_name,
                    parameter="config_type",
                    value=actual_type,
                    expected="ModelConfig"
                )
            return config
        except Exception as e:
            if isinstance(e, ModelConfigError):
                raise
            raise ModelConfigError(
                f"Failed to load model configuration: {str(e)}",
                model_name=model_name
            ) from e
    
    def get_registered_model_types(self) -> Dict[str, Type[BaseModel]]:
        """Get a copy of the registered model types.
        
        Returns:
            Dict mapping model type names to model classes
        """
        return self._registry.copy()
