"""Field-specific validation functions.

This module provides specialized validation functions for different field types
in invoice data, following the rules specified in the project ADRs.
"""

import re
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Tuple, Union


def validate_total_amount(value: Any) -> Tuple[bool, str, Optional[float]]:
    """Validate a total amount value according to ADR-001.
    
    Args:
        value: The value to validate
        
    Returns:
        Tuple of (is_valid, error_message, normalized_value)
        If valid, error_message will be empty and normalized_value will be set
    """
    if value is None:
        return False, "Total amount cannot be empty", None
        
    # Convert to string and clean
    try:
        str_val = str(value).strip()
        
        # Check pattern
        if not re.match(r'^\$?[0-9,]*\.?[0-9]*$', str_val):
            return False, f"Invalid total amount format: {value}", None
            
        # Clean and convert
        str_val = str_val.replace('$', '').replace(',', '')
        decimal_val = Decimal(str_val)
        
        # Check constraints
        if decimal_val < 0:
            return False, f"Total amount must be positive: {value}", None
            
        # Normalize to float with 2 decimal places
        float_val = float(decimal_val)
        return True, "", float_val
        
    except (ValueError, InvalidOperation, TypeError) as e:
        return False, f"Invalid total amount: {value} - {str(e)}", None


def normalize_total_amount(value: Any) -> Optional[str]:
    """Normalize a total amount value to a consistent format.
    
    Args:
        value: The value to normalize
        
    Returns:
        Normalized string in format "123.45" or None if invalid
    """
    is_valid, _, float_val = validate_total_amount(value)
    if is_valid and float_val is not None:
        return f"{float_val:.2f}"
    return None


def validate_work_order(value: Any) -> Tuple[bool, str, Optional[str]]:
    """Validate a work order number according to ADR-001.
    
    Args:
        value: The value to validate
        
    Returns:
        Tuple of (is_valid, error_message, normalized_value)
        If valid, error_message will be empty and normalized_value will be set
    """
    if value is None:
        return False, "Work order number cannot be empty", None
        
    try:
        str_val = str(value).strip()
        
        # Check pattern (5 alphanumeric characters)
        if not re.match(r'^[A-Za-z0-9]{5}$', str_val):
            return False, f"Invalid work order format: {value}. Must be exactly 5 alphanumeric characters.", None
            
        return True, "", str_val
        
    except (ValueError, TypeError) as e:
        return False, f"Invalid work order: {value} - {str(e)}", None


def normalize_work_order(value: Any) -> Optional[str]:
    """Normalize a work order number to a consistent format.
    
    Args:
        value: The value to normalize
        
    Returns:
        Normalized string or None if invalid
    """
    is_valid, _, normalized = validate_work_order(value)
    return normalized if is_valid else None


def compare_extracted_to_ground_truth(
    extracted: Dict[str, Any],
    ground_truth: Dict[str, Any]
) -> Dict[str, Dict[str, Any]]:
    """Compare extracted field values to ground truth.
    
    Args:
        extracted: Dictionary of extracted field values
        ground_truth: Dictionary of ground truth field values
        
    Returns:
        Dictionary with comparison results for each field
    """
    results = {}
    
    # Get all unique field names
    all_fields = set(list(extracted.keys()) + list(ground_truth.keys()))
    
    for field in all_fields:
        # Initialize result for this field
        field_result = {
            "extracted": extracted.get(field),
            "ground_truth": ground_truth.get(field),
            "match": False,
            "normalized_match": False,
            "normalized_extracted": None,
            "normalized_ground_truth": None,
            "missing_in_extracted": field not in extracted,
            "missing_in_ground_truth": field not in ground_truth
        }
        
        # Skip comparison if field is missing in either
        if field_result["missing_in_extracted"] or field_result["missing_in_ground_truth"]:
            results[field] = field_result
            continue
        
        # Direct string comparison
        extracted_val = str(extracted.get(field, "")).strip()
        ground_truth_val = str(ground_truth.get(field, "")).strip()
        field_result["match"] = extracted_val == ground_truth_val
        
        # Field-specific normalization and comparison
        if field.lower() in ["total", "amount", "total amount"]:
            field_result["normalized_extracted"] = normalize_total_amount(extracted.get(field))
            field_result["normalized_ground_truth"] = normalize_total_amount(ground_truth.get(field))
            
        elif field.lower() in ["work order", "work order number", "workorder"]:
            field_result["normalized_extracted"] = normalize_work_order(extracted.get(field))
            field_result["normalized_ground_truth"] = normalize_work_order(ground_truth.get(field))
            
        else:
            # Default normalization for other fields
            if extracted.get(field) is not None:
                field_result["normalized_extracted"] = str(extracted.get(field)).strip()
            if ground_truth.get(field) is not None:
                field_result["normalized_ground_truth"] = str(ground_truth.get(field)).strip()
        
        # Check normalized match
        if (field_result["normalized_extracted"] is not None and 
            field_result["normalized_ground_truth"] is not None):
            field_result["normalized_match"] = (
                field_result["normalized_extracted"] == field_result["normalized_ground_truth"]
            )
            
        results[field] = field_result
        
    return results 