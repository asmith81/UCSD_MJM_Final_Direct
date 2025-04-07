"""
Base interface for model output parsing.

This module defines the interface for parsing raw model outputs into structured data.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pathlib import Path

from ..config.base_config import BaseConfig


class OutputParserError(Exception):
    """Base exception for output parser errors."""
    pass


class OutputParsingError(OutputParserError):
    """Raised when parsing model output fails."""
    pass


class OutputValidationError(OutputParserError):
    """Raised when validation of parsed output fails."""
    pass


class BaseOutputParser(ABC):
    """Base interface for model output parsing.
    
    This interface defines how to parse and structure raw model outputs
    into a standardized format for evaluation and comparison.
    
    Implementations should:
    - Handle different output formats from various models
    - Extract structured field data
    - Normalize field names and values
    - Validate extracted data against expected formats
    """
    
    @abstractmethod
    def initialize(self, config: BaseConfig) -> None:
        """Initialize the parser with configuration.
        
        Args:
            config: Parser configuration
            
        Raises:
            OutputParserError: If initialization fails
            ValueError: If configuration is invalid
        """
        pass
        
    @abstractmethod
    def parse_output(self, model_output: str) -> Dict[str, Any]:
        """Parse raw model output into structured data.
        
        Args:
            model_output: Raw text output from a model
            
        Returns:
            Dict containing extracted field values
            
        Raises:
            OutputParsingError: If parsing fails
        """
        pass
        
    @abstractmethod
    def validate_output(self, parsed_output: Dict[str, Any]) -> bool:
        """Validate the parsed output for completeness and correctness.
        
        Args:
            parsed_output: Dictionary of parsed field values
            
        Returns:
            True if validation passes, False otherwise
        """
        pass
        
    @abstractmethod
    def normalize_output(self, parsed_output: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize field names and values in parsed output.
        
        Applies field-specific normalization to ensure consistent formats
        regardless of the original model output format.
        
        Args:
            parsed_output: Dictionary of parsed field values
            
        Returns:
            Dictionary with normalized field names and values
        """
        pass 