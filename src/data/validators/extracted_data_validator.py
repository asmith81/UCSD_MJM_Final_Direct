"""Extracted data validator implementation.

This module provides a validator for data extracted by models,
ensuring that the extracted values conform to expected formats.
"""

import logging
from typing import Any, Dict, List, Optional, Set, Tuple

from .base_validator import BaseValidator
from .field_validators import validate_total_amount, validate_work_order


class ExtractedDataValidator(BaseValidator):
    """Validator for extracted data.
    
    This validator ensures that data extracted by models meets
    expected format and type requirements.
    
    Attributes:
        expected_fields: List of fields expected to be present
        field_validators: Dictionary mapping field names to validation functions
    """
    
    # Standardized field names and their variations
    FIELD_NAME_VARIANTS = {
        "Work Order Number": [
            "Work Order Number",
            "Work Order Number/Numero de Orden",
            "Work Order",
            "Order Number",
            "Numero de Orden"
        ],
        "Total": [
            "Total",
            "Total Amount",
            "Invoice Total",
            "Amount"
        ]
    }
    
    def __init__(
        self,
        expected_fields: Optional[List[str]] = None,
        strict_mode: bool = True
    ) -> None:
        """Initialize the extracted data validator.
        
        Args:
            expected_fields: List of fields expected in the data (default: ["Total", "Work Order Number"])
            strict_mode: Whether to use strict validation (default: True)
        """
        super().__init__(strict_mode=strict_mode)
        self.expected_fields = expected_fields or ["Total", "Work Order Number"]
        
        # Set up field-specific validators
        self.field_validators = {
            "Total": validate_total_amount,
            "Work Order Number": validate_work_order
        }
        
        self._logger = logging.getLogger(__name__)
        
    def _normalize_field_name(self, field_name: str) -> str:
        """Normalize field names to handle variations.
        
        Args:
            field_name: Field name to normalize
            
        Returns:
            Normalized (standardized) field name
        """
        field_name = field_name.strip()
        
        # Check if the field matches any of our known variants
        for standard_name, variants in self.FIELD_NAME_VARIANTS.items():
            if field_name in variants:
                return standard_name
                
        # If no match found, return the original name
        return field_name
        
    def _normalize_data_keys(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize data keys to handle field name variations.
        
        Args:
            data: Data dictionary with possibly non-standardized field names
            
        Returns:
            New dictionary with standardized field names
        """
        normalized_data = {}
        
        # Create a map of variations to standard names
        variant_map = {}
        for std_name, variants in self.FIELD_NAME_VARIANTS.items():
            for variant in variants:
                variant_map[variant] = std_name
        
        # Process each field in the data
        for field_name, value in data.items():
            # Clean up field name
            clean_name = field_name.strip()
            
            # Check if it's a known variant
            if clean_name in variant_map:
                std_name = variant_map[clean_name]
                normalized_data[std_name] = value
            else:
                # Keep original name if not a known variant
                normalized_data[clean_name] = value
                
        return normalized_data
        
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate extracted data.
        
        Args:
            data: Dictionary of extracted field values
            
        Returns:
            True if validation passes, False otherwise
        """
        self.clear_errors()
        
        # Normalize field names to handle variations
        normalized_data = self._normalize_data_keys(data)
        
        # Check for expected fields
        missing_fields = set(self.expected_fields) - set(normalized_data.keys())
        if missing_fields:
            self.add_error(f"Missing expected fields: {missing_fields}")
            
        # Validate each field using field-specific validators
        for field, value in normalized_data.items():
            if field in self.field_validators:
                validator = self.field_validators[field]
                is_valid, error_msg, _ = validator(value)
                
                if not is_valid:
                    self.add_error(f"Invalid {field}: {error_msg}")
                    
        valid = not self.has_errors()
        self._logger.info(f"Extracted data validation {'passed' if valid else 'failed'}")
        
        return valid
        
    def add_field_validator(self, field_name: str, validator_func: Any) -> None:
        """Add a custom field validator.
        
        Args:
            field_name: Name of the field to validate
            validator_func: Validation function that returns (is_valid, error_msg, normalized_value)
        """
        self.field_validators[field_name] = validator_func
        self._logger.debug(f"Added validator for field: {field_name}")
        
    def get_field_validation_results(self, data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Get detailed validation results for each field.
        
        Args:
            data: Dictionary of extracted field values
            
        Returns:
            Dictionary mapping field names to validation results
        """
        results = {}
        
        # Normalize field names
        normalized_data = self._normalize_data_keys(data)
        
        # Track which original fields map to which normalized fields for reporting
        original_to_normalized = {}
        for orig_field in data:
            norm_field = self._normalize_field_name(orig_field)
            original_to_normalized[orig_field] = norm_field
        
        # Validate each field
        for field, value in normalized_data.items():
            if field in self.field_validators:
                validator = self.field_validators[field]
                is_valid, error_msg, normalized = validator(value)
                
                results[field] = {
                    "original": value,
                    "original_field_name": next((k for k, v in original_to_normalized.items() if v == field), field),
                    "valid": is_valid,
                    "error": error_msg if not is_valid else "",
                    "normalized": normalized
                }
            else:
                # For fields without specific validators, just check if not None
                results[field] = {
                    "original": value,
                    "original_field_name": next((k for k, v in original_to_normalized.items() if v == field), field),
                    "valid": value is not None,
                    "error": "No value provided" if value is None else "",
                    "normalized": str(value).strip() if value is not None else None
                }
                
        # Check for missing fields
        for field in self.expected_fields:
            if field not in normalized_data:
                results[field] = {
                    "original": None,
                    "original_field_name": None,
                    "valid": False,
                    "error": "Field missing in extracted data",
                    "normalized": None
                }
                
        return results 