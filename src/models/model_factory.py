"""
Factory for creating model instances.

This module provides a factory for creating and initializing model instances
based on configuration. It handles dependency injection, configuration validation,
and proper error handling.
"""
from typing import Dict, Type, Any, Optional
from pathlib import Path
import logging

from .base_model import BaseModel
from .model_errors import (
    ModelError,
    ModelInitializationError,
    ModelConfigError,
    ModelResourceError,
    ModelCreationError
)
from ..config.base_config import BaseConfig
from ..config import get_config_manager, ConfigType
from ..config.implementations.model_config import ModelConfig

# Set up logger for this module
logger = logging.getLogger(__name__)

class ModelFactory:
    """
    Factory for creating model instances based on configuration.
    Uses dependency injection and configuration management.
    
    Example:
        # Register a model implementation
        ModelFactory.register_model("custom_model", CustomModel)
        
        # Create a factory instance with configuration manager
        config_manager = get_config_manager()
        factory = ModelFactory(config_manager)
        
        # Create a model instance
        model = factory.create_model("model_name")
    """

    # Registry of available model implementations
    MODEL_REGISTRY: Dict[str, Type[BaseModel]] = {}

    def __init__(self, config_manager):
        """
        Initialize the factory with required dependencies.

        Args:
            config_manager: Configuration manager instance.
        
        Raises:
            ValueError: If config_manager is None
        """
        if config_manager is None:
            raise ValueError("config_manager is required")
        self._config_manager = config_manager

    def create_model(self, model_name: str, model_config: Optional[BaseConfig] = None) -> BaseModel:
        """
        Create and initialize a model instance.

        This method:
        1. Loads/validates configuration
        2. Creates model instance
        3. Initializes the model
        4. Verifies initialization

        Args:
            model_name: Name of the model to create
            model_config: Optional explicit configuration. If not provided,
                        will load from config manager using model_name.

        Returns:
            BaseModel: The initialized model instance

        Raises:
            ModelCreationError: If model creation or initialization fails
            ModelConfigError: If configuration is invalid
            ModelResourceError: If required resources cannot be loaded
            ValueError: If model type is not supported (deprecated)
        """
        model_type = None
        try:
            logger.info(f"Creating model '{model_name}'")
            
            # Get configuration
            try:
                config = model_config or self._load_model_config(model_name)
            except Exception as e:
                raise ModelConfigError(
                    f"Failed to load configuration: {str(e)}",
                    model_name=model_name
                ) from e
            
            # Validate model type
            try:
                model_type = config.get_value("type")
                if not model_type:
                    raise ModelConfigError(
                        "Model type not specified in configuration",
                        model_name=model_name,
                        parameter="type"
                    )
                    
                if model_type not in self.MODEL_REGISTRY:
                    available_types = ", ".join(self.MODEL_REGISTRY.keys())
                    raise ModelCreationError(
                        f"Unsupported model type. Available types: {available_types}",
                        model_name=model_name,
                        model_type=model_type
                    )
            except (KeyError, AttributeError) as e:
                raise ModelConfigError(
                    f"Invalid configuration structure: {str(e)}",
                    model_name=model_name
                ) from e

            # Create model instance
            try:
                model_class = self.MODEL_REGISTRY[model_type]
                model = model_class()
                logger.debug(f"Created instance of {model_class.__name__}")
            except Exception as e:
                raise ModelCreationError(
                    f"Failed to instantiate model class: {str(e)}",
                    model_name=model_name,
                    model_type=model_type,
                    cause=e
                ) from e

            # Validate configuration
            try:
                if not model.validate_config(config):
                    raise ModelConfigError(
                        "Configuration validation failed",
                        model_name=model_name,
                        parameter="<multiple>"
                    )
            except Exception as e:
                if isinstance(e, ModelConfigError):
                    raise
                raise ModelConfigError(
                    f"Configuration validation error: {str(e)}",
                    model_name=model_name
                ) from e
            
            # Initialize model
            try:
                model.initialize(config)
                logger.info(f"Successfully initialized model '{model_name}' (type: {model_type})")
                return model
            except Exception as e:
                if isinstance(e, (ModelInitializationError, ModelResourceError)):
                    raise
                raise ModelInitializationError(
                    f"Initialization error: {str(e)}",
                    model_name=model_name
                ) from e

        except ModelError as e:
            # Already a specific model error, just log and re-raise
            logger.error(f"Model error: {str(e)}")
            raise
        except Exception as e:
            # Unexpected error, wrap in ModelCreationError
            error_msg = f"Unexpected error creating model '{model_name}': {str(e)}"
            logger.exception(error_msg)
            raise ModelCreationError(
                error_msg, 
                model_name=model_name,
                model_type=model_type,
                cause=e
            ) from e

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
                raise ModelConfigError(
                    f"Invalid configuration type: expected ModelConfig, got {type(config).__name__}",
                    model_name=model_name
                )
            return config
        except Exception as e:
            if isinstance(e, ModelConfigError):
                raise
            raise ModelConfigError(
                f"Failed to load configuration: {str(e)}",
                model_name=model_name
            ) from e

    @classmethod
    def register_model(cls, model_type: str, model_class: Type[BaseModel]) -> None:
        """
        Register a new model implementation.

        Args:
            model_type: Type identifier for the model
            model_class: Model class implementing BaseModel

        Raises:
            ValueError: If model_type is invalid or model_class doesn't implement BaseModel
        """
        if not model_type or not isinstance(model_type, str):
            raise ValueError("Model type must be a non-empty string")
        
        if not isinstance(model_class, type) or not issubclass(model_class, BaseModel):
            raise ValueError("Model class must implement BaseModel interface")

        logger.debug(f"Registering model type '{model_type}' with implementation {model_class.__name__}")
        cls.MODEL_REGISTRY[model_type] = model_class
