"""
Models package for invoice data extraction.

This package contains model interfaces, factory, and error handling components.
"""

# Import base components
from .base_model import BaseModel
from .model_factory import ModelFactory
from .base_output_parser import BaseOutputParser, OutputParserError, OutputParsingError, OutputValidationError
from .output_parser_factory import OutputParserFactory, OutputParserCreationError
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
    'BaseOutputParser',
    'OutputParserFactory',
    'OutputParserError',
    'OutputParsingError',
    'OutputValidationError',
    'OutputParserCreationError',
    'ModelError',
    'ModelInitializationError',
    'ModelConfigError',
    'ModelProcessingError',
    'ModelResourceError',
    'ModelInputError',
    'ModelTimeoutError',
    'ModelCreationError'
]
