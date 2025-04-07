"""
Models package for invoice data extraction.

This package contains model interfaces, factory, and error handling components.
"""

# Import base components
from .base_model import BaseModel
from .model_factory import ModelFactory
from .model_errors import (
    ModelError, 
    ModelInitializationError,
    ModelConfigError,
    ModelProcessingError,
    ModelResourceError,
    ModelInputError,
    ModelTimeoutError,
    ModelCreationError
)

# Model registration will be done by specific model implementations

__all__ = [
    'BaseModel',
    'ModelFactory',
    'ModelError',
    'ModelInitializationError',
    'ModelConfigError',
    'ModelProcessingError',
    'ModelResourceError',
    'ModelInputError',
    'ModelTimeoutError',
    'ModelCreationError'
]
