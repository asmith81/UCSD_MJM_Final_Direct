"""
Models Package.

This package contains model implementations and utilities for working with models,
including error handling, resource management, and model loading.
"""

from .base_model import BaseModel
from .base_model_impl import BaseModelImpl
from .model_factory import ModelFactory
from .model_errors import (
    ModelError,
    ModelInitializationError,
    ModelConfigError,
    ModelProcessingError,
    ModelResourceError,
    ModelInputError,
    ModelTimeoutError,
    ModelLoaderTimeoutError,
    ModelCreationError
)
from .model_resource_manager import ModelResourceManager
from .retry_utils import RetryConfig, with_retry, create_retryable_function
from .error_recovery import ErrorRecoveryManager, with_error_recovery
from .model_loading_timeout import TimeoutHandler, load_model_with_timeout

__all__ = [
    # Base interfaces
    'BaseModel',
    'BaseModelImpl',
    
    # Factory
    'ModelFactory',
    
    # Error classes
    'ModelError',
    'ModelInitializationError',
    'ModelConfigError',
    'ModelProcessingError',
    'ModelResourceError',
    'ModelInputError',
    'ModelTimeoutError',
    'ModelLoaderTimeoutError',
    'ModelCreationError',
    
    # Resource management
    'ModelResourceManager',
    
    # Retry utilities
    'RetryConfig',
    'with_retry',
    'create_retryable_function',
    
    # Error recovery
    'ErrorRecoveryManager',
    'with_error_recovery',
    
    # Timeout handling
    'TimeoutHandler',
    'load_model_with_timeout'
]
