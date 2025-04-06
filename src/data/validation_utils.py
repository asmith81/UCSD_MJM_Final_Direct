"""Common validation utility functions.

This module provides utility functions for data validation across
the invoice extraction system.
"""

import os
import pandas as pd
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, Set

from .validators.field_validators import (
    validate_total_amount,
    validate_work_order,
    normalize_total_amount,
    normalize_work_order,
    compare_extracted_to_ground_truth
)


def validate_directory_exists(directory_path: Union[str, Path]) -> Tuple[bool, str]:
    """Validate that a directory exists.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    path = Path(directory_path)
    if not path.exists():
        return False, f"Directory does not exist: {path}"
    if not path.is_dir():
        return False, f"Path is not a directory: {path}"
    return True, ""


def validate_file_exists(file_path: Union[str, Path]) -> Tuple[bool, str]:
    """Validate that a file exists.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    path = Path(file_path)
    if not path.exists():
        return False, f"File does not exist: {path}"
    if not path.is_file():
        return False, f"Path is not a file: {path}"
    return True, ""


def validate_csv_file(file_path: Union[str, Path]) -> Tuple[bool, str, Optional[pd.DataFrame]]:
    """Validate a CSV file and load it if valid.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Tuple of (is_valid, error_message, dataframe)
        If valid, error_message will be empty and dataframe will be set
    """
    # First check file exists
    is_valid, error_msg = validate_file_exists(file_path)
    if not is_valid:
        return False, error_msg, None
        
    # Try to read as CSV
    try:
        df = pd.read_csv(file_path)
        return True, "", df
    except Exception as e:
        return False, f"Invalid CSV file: {str(e)}", None


def validate_image_directory(directory_path: Union[str, Path], file_extensions: Set[str] = None) -> Dict[str, Any]:
    """Validate an image directory and get statistics.
    
    Args:
        directory_path: Path to the directory containing images
        file_extensions: Set of valid file extensions (default: {'.jpg', '.jpeg', '.png'})
        
    Returns:
        Dictionary with validation results and statistics
    """
    # Set default extensions
    file_extensions = file_extensions or {'.jpg', '.jpeg', '.png'}
    
    # Check directory exists
    is_valid, error_msg = validate_directory_exists(directory_path)
    if not is_valid:
        return {
            "valid": False,
            "error": error_msg,
            "image_count": 0,
            "images": []
        }
        
    # Get all files
    path = Path(directory_path)
    all_files = list(path.glob('*'))
    
    # Check image files
    image_files = [f for f in all_files if f.suffix.lower() in file_extensions]
    
    result = {
        "valid": len(image_files) > 0,
        "error": "" if len(image_files) > 0 else "No image files found",
        "directory": str(path),
        "image_count": len(image_files),
        "by_extension": {},
        "images": [str(f) for f in image_files]
    }
    
    # Count by extension
    for ext in file_extensions:
        ext_files = [f for f in image_files if f.suffix.lower() == ext]
        result["by_extension"][ext] = len(ext_files)
        
    return result


def get_data_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """Get comprehensive statistics about a DataFrame.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Dictionary with statistics
    """
    stats = {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": {col: int(count) for col, count in df.isnull().sum().items()},
        "unique_values": {col: int(df[col].nunique()) for col in df.columns},
        "sample_values": {col: list(df[col].dropna().head(3).values) for col in df.columns},
    }
    
    # Add numeric column statistics if available
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        stats["numeric_stats"] = {
            col: {
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "mean": float(df[col].mean()),
                "median": float(df[col].median()),
                "std": float(df[col].std())
            } for col in numeric_cols
        }
        
    return stats


def validate_extracted_fields(extracted: Dict[str, Any], ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    """Validate extracted fields against ground truth.
    
    This is a wrapper around compare_extracted_to_ground_truth that adds
    summary statistics.
    
    Args:
        extracted: Dictionary of extracted field values
        ground_truth: Dictionary of ground truth field values
        
    Returns:
        Dictionary with validation results
    """
    # Get detailed comparison by field
    field_results = compare_extracted_to_ground_truth(extracted, ground_truth)
    
    # Calculate summary statistics
    exact_matches = sum(1 for field, result in field_results.items() 
                      if result["match"])
    normalized_matches = sum(1 for field, result in field_results.items() 
                           if result["normalized_match"])
    total_fields = len(field_results)
    
    # Fields present in both
    common_fields = [field for field in field_results 
                    if not field_results[field]["missing_in_extracted"] 
                    and not field_results[field]["missing_in_ground_truth"]]
    common_count = len(common_fields)
    
    summary = {
        "exact_match_rate": exact_matches / total_fields if total_fields > 0 else 0,
        "normalized_match_rate": normalized_matches / total_fields if total_fields > 0 else 0,
        "common_field_match_rate": (sum(1 for field in common_fields 
                                      if field_results[field]["normalized_match"]) / common_count) 
                                  if common_count > 0 else 0,
        "extracted_fields_count": len(extracted),
        "ground_truth_fields_count": len(ground_truth),
        "total_fields_count": total_fields,
        "common_fields_count": common_count,
        "missing_in_extracted": [field for field in field_results 
                               if field_results[field]["missing_in_extracted"]],
        "missing_in_ground_truth": [field for field in field_results 
                                  if field_results[field]["missing_in_ground_truth"]],
        "field_results": field_results
    }
    
    return summary 