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
        self._retry_config = RetryConfig(
            max_attempts=2,
            delay_seconds=1.0,
            backoff_factor=2.0,
            max_delay_seconds=10.0,
            non_retryable_exceptions=[
                ModelConfigError,  # Configuration errors shouldn't be retried
                ModelCreationError  # Creation errors typically won't be resolved by retry
            ]
        )

    @with_error_recovery(operation_name="create_model")
    @with_retry()
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
            ModelInitializationError: If model initialization fails
            ModelLoaderTimeoutError: If model loading times out
        """
        model_type = None
        recovery_manager = ErrorRecoveryManager(model_name=model_name)
        
        try:
            logger.info(f"Creating model '{model_name}'")
            
            # Get configuration
            try:
                config = model_config or self._load_model_config(model_name)
            except Exception as e:
                if isinstance(e, ModelConfigError):
                    raise
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
                
                # Register cleanup if initialization fails
                def cleanup_model():
                    logger.debug(f"Cleaning up model instance during error recovery")
                    if hasattr(model, '_cleanup_resources'):
                        model._cleanup_resources()
                
                recovery_manager.register_recovery_action(cleanup_model)
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
                    # Don't wrap ModelConfigError with a ModelCreationError
                    # This allows the original error to propagate
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
                # Preserve the original error types for better error handling
                # ModelInitializationError, ModelResourceError, and ModelLoaderTimeoutError should propagate directly
                if isinstance(e, (ModelInitializationError, ModelResourceError, ModelLoaderTimeoutError)):
                    raise
                # If it's some other exception, wrap in ModelInitializationError 
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
    
    @classmethod
    def register_model(cls, model_type: str, model_class: Type[BaseModel]) -> None:
        """
        Register a model implementation with the factory.

        Args:
            model_type: String identifier for the model type
            model_class: Model class implementing BaseModel
            
        Raises:
            ValueError: If model_type is already registered
        """
        if model_type in cls.MODEL_REGISTRY:
            raise ValueError(f"Model type '{model_type}' is already registered")
            
        if not issubclass(model_class, BaseModel):
            raise ValueError(f"Model class must implement BaseModel interface")
            
        cls.MODEL_REGISTRY[model_type] = model_class
        logger.debug(f"Registered model implementation: {model_type} -> {model_class.__name__}")
    
    @classmethod
    def get_registered_model_types(cls) -> Dict[str, Type[BaseModel]]:
        """Get a copy of the registered model types.
        
        Returns:
            Dict mapping model type names to model classes
        """
        return cls.MODEL_REGISTRY.copy()
