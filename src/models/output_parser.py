"""
Output parser module.

This module provides the main entry point for output parsing functionality,
exposing the implemented parsers and factory.
"""

from .base_output_parser import (
    BaseOutputParser,
    OutputParserError,
    OutputParsingError,
    OutputValidationError
)
from .output_parser_factory import OutputParserFactory
from .output_parser.implementations.extracted_fields_parser import ExtractedFieldsOutputParser


# Register the default implementation
OutputParserFactory.register_parser("default", ExtractedFieldsOutputParser)
OutputParserFactory.register_parser("extracted_fields", ExtractedFieldsOutputParser)


# No need to define create_parser here, as we've moved it to __init__.py
# to avoid circular imports


__all__ = [
    'BaseOutputParser',
    'OutputParserError',
    'OutputParsingError',
    'OutputValidationError',
    'OutputParserFactory',
    'ExtractedFieldsOutputParser',
]
