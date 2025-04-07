"""
Output parser implementations.

This module provides concrete implementations of the BaseOutputParser interface
for different types of model outputs.
"""

from .extracted_fields_parser import ExtractedFieldsOutputParser

__all__ = [
    'ExtractedFieldsOutputParser',
] 