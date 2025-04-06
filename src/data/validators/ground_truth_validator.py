"""Ground truth validator implementation.

This module provides a validator for ground truth data, ensuring that
the data meets the required format and quality standards.
"""

import pandas as pd
import logging
from typing import Any, Dict, List, Optional, Set, Tuple

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
    
    # List of possible work order column names
    WORK_ORDER_COLUMN_NAMES = [
        "Work Order Number",
        "Work Order Number/Numero de Orden",
        "Work Order Number/Numero de Orden"
    ]
    
    def __init__(
        self,
        required_columns: Optional[List[str]] = None,
        strict_mode: bool = True
    ) -> None:
        """Initialize the ground truth validator.
        
        Args:
            required_columns: List of required columns (default based on standard column names)
            strict_mode: Whether to use strict validation (default: True)
        """
        super().__init__(strict_mode=strict_mode)
        self._logger = logging.getLogger(__name__)
        
        # Set default required columns
        if required_columns is None:
            self.required_columns = ["Invoice", self.WORK_ORDER_COLUMN_NAMES[0], "Total"]
        else:
            self.required_columns = required_columns
        
    def _get_actual_work_order_column(self, data: pd.DataFrame) -> Optional[str]:
        """Find the actual work order column name in the DataFrame.
        
        Args:
            data: DataFrame to search for work order column
            
        Returns:
            The actual column name if found, otherwise None
        """
        for col_name in self.WORK_ORDER_COLUMN_NAMES:
            if col_name in data.columns:
                return col_name
        return None
        
    def validate(self, data: pd.DataFrame) -> bool:
        """Validate the ground truth data.
        
        This method checks that:
        1. All required columns are present (with column name flexibility)
        2. No missing values in required fields
        3. Invoice IDs are unique
        4. Field values match required formats
        
        Args:
            data: Ground truth DataFrame to validate
            
        Returns:
            True if validation passes, False otherwise
        """
        self.clear_errors()
        
        # Try to find the work order column if it has a different name
        actual_work_order_col = self._get_actual_work_order_column(data)
        actual_required_columns = self.required_columns.copy()
        
        # Update required columns with actual work order column name if found
        if actual_work_order_col and actual_work_order_col != self.WORK_ORDER_COLUMN_NAMES[0]:
            self._logger.info(f"Found work order column with name: {actual_work_order_col}")
            # Replace the standard name with the actual column name in required columns
            for i, col in enumerate(actual_required_columns):
                if col == self.WORK_ORDER_COLUMN_NAMES[0]:
                    actual_required_columns[i] = actual_work_order_col
                    break
        
        # Check required columns
        missing_cols = set(actual_required_columns) - set(data.columns)
        if missing_cols:
            self.add_error(f"Missing required columns: {missing_cols}")
            return not self.strict_mode
            
        # Check for missing values in required columns
        missing_values = data[actual_required_columns].isnull().any()
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
        
        # Get the actual work order column to use
        work_order_col = actual_work_order_col or self.WORK_ORDER_COLUMN_NAMES[0]
        
        for idx, row in data.iterrows():
            # Validate Total
            if 'Total' in data.columns:
                is_valid, error_msg, _ = validate_total_amount(row['Total'])
                if not is_valid:
                    invalid_totals.append(f"Row {idx + 1}: {error_msg}")
                    
            # Validate Work Order Number using the correct column name
            if work_order_col in data.columns:
                is_valid, error_msg, _ = validate_work_order(row[work_order_col])
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
        # Find the actual work order column first for better validation
        actual_work_order_col = self._get_actual_work_order_column(data)
        if actual_work_order_col and actual_work_order_col != self.WORK_ORDER_COLUMN_NAMES[0]:
            # Temporarily update required columns for accurate validation
            original_required = self.required_columns.copy()
            self.required_columns = [
                col if col != self.WORK_ORDER_COLUMN_NAMES[0] else actual_work_order_col
                for col in self.required_columns
            ]
            
            result = self._get_validation_statistics_impl(data)
            
            # Restore original required columns
            self.required_columns = original_required
            return result
        else:
            return self._get_validation_statistics_impl(data)
    
    def _get_validation_statistics_impl(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Implementation of validation statistics generation.
        
        Args:
            data: Ground truth DataFrame to analyze
            
        Returns:
            Dictionary with validation statistics
        """
        if not self.validate(data):
            self._logger.warning("Generating statistics for invalid data")
            
        # Find the actual invoice column or default to "Invoice"
        invoice_col = "Invoice" if "Invoice" in data.columns else None
            
        stats = {
            "total_rows": len(data),
            "columns": list(data.columns),
            "required_columns_present": all(col in data.columns for col in self.required_columns),
            "missing_values_by_column": data.isnull().sum().to_dict(),
            "total_missing_values": data.isnull().sum().sum(),
            "unique_invoice_count": data[invoice_col].nunique() if invoice_col else 0,
            "valid": not self.has_errors(),
            "errors": self.get_errors()
        }
        
        return stats 