"""
Extracted fields output parser implementation.

This module provides a parser for extracting structured field data from model outputs,
designed to handle various output formats and normalize field names and values.
"""
import logging
import re
import json
from typing import Any, Dict, List, Tuple, Optional, Pattern, Match

from ...base_output_parser import BaseOutputParser, OutputParsingError, OutputValidationError
from ....config.base_config import BaseConfig
from ....data.validators.extracted_data_validator import ExtractedDataValidator
from ....data.validators.field_validators import (
    validate_total_amount,
    validate_work_order,
    normalize_total_amount,
    normalize_work_order
)


class ExtractedFieldsOutputParser(BaseOutputParser):
    """
    Parser for extracting structured fields from model outputs.
    
    This implementation can handle various output formats:
    - Plain text with field names and values
    - JSON-formatted output
    - Key-value pairs in different formats
    
    It normalizes field names to handle variations and validates values.
    
    Examples of supported formats:
        "Work Order Number: 12345, Total Amount: $123.45"
        "{'work_order': '12345', 'total': 123.45}"
        "Work Order: 12345\nTotal: $123.45"
    """
    
    # Field name variants mapping to standardized names
    FIELD_NAME_VARIANTS = {
        "work_order": [
            "work_order", "work order", "workorder", "work order number",
            "work_order_number", "workordernumber", "order number", "order_number",
            "wo", "wo number", "wo #"
        ],
        "total_amount": [
            "total_amount", "total amount", "amount", "total", "price", "cost",
            "total cost", "total price", "invoice amount", "invoice total"
        ]
    }
    
    # Regular expressions for extracting field values
    FIELD_PATTERNS = {
        "key_value": re.compile(r'(?:^|\n|,)\s*([^:,\n]+)\s*:\s*([^,\n]+)'),
        "json_pattern": re.compile(r'({[\s\S]*}|\[[\s\S]*\])'),
    }
    
    def __init__(self, data_validator: Optional[ExtractedDataValidator] = None):
        """
        Initialize the parser with optional dependencies.
        
        Args:
            data_validator: Optional validator for extracted data.
                          If not provided, a default one will be created.
        """
        self._data_validator = data_validator or self._create_default_validator()
        self._logger = logging.getLogger(__name__)
        self._config = None
    
    def initialize(self, config: BaseConfig) -> None:
        """
        Initialize the parser with configuration.
        
        Args:
            config: Parser configuration
            
        Raises:
            ValueError: If configuration is invalid
        """
        self._config = config
        self._logger.info("Initialized ExtractedFieldsOutputParser with configuration")
    
    def parse_output(self, model_output: str) -> Dict[str, Any]:
        """
        Parse model output text into structured field data.
        
        Args:
            model_output: Raw text output from a model
            
        Returns:
            Dict containing extracted field values
            
        Raises:
            OutputParsingError: If parsing fails
        """
        if not model_output or not isinstance(model_output, str):
            raise OutputParsingError("Model output must be a non-empty string")
        
        self._logger.debug(f"Parsing model output: {model_output[:100]}...")
        
        # Try various parsing strategies in order
        parsed = None
        
        # Try JSON parsing first
        parsed = self._try_json_parsing(model_output)
        if parsed:
            return parsed
        
        # Try key-value parsing
        parsed = self._try_key_value_parsing(model_output)
        if parsed:
            return parsed
        
        # If all parsing methods fail
        self._logger.warning("Failed to parse model output with any method")
        raise OutputParsingError("Could not parse model output into structured data")
    
    def validate_output(self, parsed_output: Dict[str, Any]) -> bool:
        """
        Validate the parsed output for completeness and correctness.
        
        Args:
            parsed_output: Dictionary of parsed field values
            
        Returns:
            True if validation passes, False otherwise
        """
        if not parsed_output:
            self._logger.warning("Empty parsed output")
            return False
        
        return self._data_validator.validate(parsed_output)
    
    def normalize_output(self, parsed_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize field names and values in parsed output.
        
        Args:
            parsed_output: Dictionary of parsed field values
            
        Returns:
            Dictionary with normalized field names and values
        """
        normalized = {}
        
        # Normalize field names to handle variations
        for field, value in parsed_output.items():
            normalized_field = self._normalize_field_name(field)
            
            # If we have a specific normalizer for this field, use it
            if normalized_field == "work_order":
                _, _, normalized_value = validate_work_order(value)
                normalized[normalized_field] = normalized_value
            elif normalized_field == "total_amount":
                _, _, normalized_value = validate_total_amount(value)
                normalized[normalized_field] = normalized_value
            else:
                # For other fields, just use the value as is
                normalized[normalized_field] = value
        
        return normalized
    
    def _create_default_validator(self) -> ExtractedDataValidator:
        """
        Create a default data validator with standard field validators.
        
        Returns:
            Configured ExtractedDataValidator instance
        """
        validator = ExtractedDataValidator(
            expected_fields=["work_order", "total_amount"],
            strict_mode=False
        )
        
        # Add standard field validators
        validator.add_field_validator("work_order", validate_work_order)
        validator.add_field_validator("total_amount", validate_total_amount)
        
        return validator
    
    def _normalize_field_name(self, field_name: str) -> str:
        """
        Normalize field names to handle variations.
        
        Args:
            field_name: Field name to normalize
            
        Returns:
            Normalized (standardized) field name
        """
        if not field_name:
            return ""
            
        field_name = str(field_name).strip().lower()
        
        # Check if the field matches any of our known variants
        for standard_name, variants in self.FIELD_NAME_VARIANTS.items():
            if field_name in variants:
                return standard_name
                
        # If no match found, return the original name
        return field_name
    
    def _try_json_parsing(self, model_output: str) -> Optional[Dict[str, Any]]:
        """
        Try to parse model output as JSON.
        
        Args:
            model_output: Raw model output text
            
        Returns:
            Parsed dictionary or None if parsing fails
        """
        # First, try to extract JSON from the text if it's mixed with other content
        json_match = self.FIELD_PATTERNS["json_pattern"].search(model_output)
        if json_match:
            json_str = json_match.group(0)
            try:
                parsed = json.loads(json_str)
                if isinstance(parsed, dict):
                    self._logger.debug("Successfully parsed JSON output")
                    return parsed
                elif isinstance(parsed, list) and len(parsed) > 0 and isinstance(parsed[0], dict):
                    self._logger.debug("Successfully parsed JSON array output")
                    return parsed[0]  # Take the first item if it's a list of objects
            except json.JSONDecodeError:
                self._logger.debug("Failed to parse as JSON - not valid JSON format")
        
        # If no JSON pattern found or parsing failed, try direct JSON parsing
        try:
            parsed = json.loads(model_output)
            if isinstance(parsed, dict):
                self._logger.debug("Successfully parsed direct JSON output")
                return parsed
        except json.JSONDecodeError:
            self._logger.debug("Failed to parse as direct JSON")
        
        return None
    
    def _try_key_value_parsing(self, model_output: str) -> Optional[Dict[str, Any]]:
        """
        Try to parse model output as key-value pairs.
        
        Args:
            model_output: Raw model output text
            
        Returns:
            Parsed dictionary or None if parsing fails
        """
        # Use regex to find key-value pairs
        matches = self.FIELD_PATTERNS["key_value"].findall(model_output)
        
        if matches:
            result = {}
            for key, value in matches:
                key = key.strip().lower()
                value = value.strip()
                normalized_key = self._normalize_field_name(key)
                
                if normalized_key:
                    result[normalized_key] = value
            
            if result:
                self._logger.debug(f"Successfully parsed key-value output: {result}")
                return result
        
        self._logger.debug("Failed to parse as key-value pairs")
        return None 