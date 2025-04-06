"""Ground truth validator implementation.

This module provides a validator for ground truth data, ensuring that
the data meets the required format and quality standards.
"""

import pandas as pd
import logging
from typing import Any, Dict, List, Optional, Set

from .base_validator import BaseValidator
from .field_validators import validate_total_amount, validate_work_order


class GroundTruthValidator(BaseValidator):
    """Validator for ground truth data.
    
    This validator ensures that ground truth data conforms to the
    required format and field specifications.
    
    Attributes:
        required_columns: List of columns that must be present
        validation_errors: List of validation errors found
    """
    
    def __init__(
        self,
        required_columns: Optional[List[str]] = None,
        strict_mode: bool = True
    ) -> None:
        """Initialize the ground truth validator.
        
        Args:
            required_columns: List of required columns (default: ["Invoice", "Work Order Number", "Total"])
            strict_mode: Whether to use strict validation (default: True)
        """
        super().__init__(strict_mode=strict_mode)
        self.required_columns = required_columns or ["Invoice", "Work Order Number", "Total"]
        self._logger = logging.getLogger(__name__)
        
    def validate(self, data: pd.DataFrame) -> bool:
        """Validate the ground truth data.
        
        This method checks that:
        1. All required columns are present
        2. No missing values in required fields
        3. Invoice IDs are unique
        4. Field values match required formats
        
        Args:
            data: Ground truth DataFrame to validate
            
        Returns:
            True if validation passes, False otherwise
        """
        self.clear_errors()
        
        # Check required columns
        missing_cols = set(self.required_columns) - set(data.columns)
        if missing_cols:
            self.add_error(f"Missing required columns: {missing_cols}")
            return not self.strict_mode
            
        # Check for missing values in required columns
        missing_values = data[self.required_columns].isnull().any()
        if missing_values.any():
            problem_cols = missing_values[missing_values].index.tolist()
            self.add_error(f"Missing values in required columns: {problem_cols}")
            
        # Check for unique invoice IDs
        if data["Invoice"].duplicated().any():
            dupes = data[data["Invoice"].duplicated()]["Invoice"].tolist()
            self.add_error(f"Duplicate invoice IDs found: {dupes}")
            
        # Validate field formats
        invalid_totals: List[str] = []
        invalid_work_orders: List[str] = []
        
        for idx, row in data.iterrows():
            # Validate Total
            if 'Total' in data.columns:
                is_valid, error_msg, _ = validate_total_amount(row['Total'])
                if not is_valid:
                    invalid_totals.append(f"Row {idx + 1}: {error_msg}")
                    
            # Validate Work Order Number
            if 'Work Order Number' in data.columns:
                is_valid, error_msg, _ = validate_work_order(row['Work Order Number'])
                if not is_valid:
                    invalid_work_orders.append(f"Row {idx + 1}: {error_msg}")
                    
        if invalid_totals:
            self.add_error("Invalid Total Amount values:\n" + "\n".join(invalid_totals))
            
        if invalid_work_orders:
            self.add_error("Invalid Work Order values:\n" + "\n".join(invalid_work_orders))
            
        valid = not self.has_errors()
        self._logger.info(f"Ground truth validation {'passed' if valid else 'failed'}")
        
        return valid
        
    def get_validation_statistics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Get statistics on the ground truth data quality.
        
        Args:
            data: Ground truth DataFrame to analyze
            
        Returns:
            Dictionary with validation statistics
        """
        if not self.validate(data):
            self._logger.warning("Generating statistics for invalid data")
            
        stats = {
            "total_rows": len(data),
            "columns": list(data.columns),
            "required_columns_present": all(col in data.columns for col in self.required_columns),
            "missing_values_by_column": data.isnull().sum().to_dict(),
            "total_missing_values": data.isnull().sum().sum(),
            "unique_invoice_count": data["Invoice"].nunique() if "Invoice" in data.columns else 0,
            "valid": not self.has_errors(),
            "errors": self.get_errors()
        }
        
        return stats 