"""Ground truth data validation and management.

This module provides the GroundTruthManager class for validating and managing
ground truth data for invoice OCR evaluation.

Field Specifications:
    Total Amount:
        - Stored as float with 2 decimal places
        - Cleaned during load (strips "$" and "," characters)
        - Must be positive number
        
    Work Order Number:
        - Stored as string (object)
        - Preserves exact format including leading zeros
        - Allows alphanumeric values

See docs/adr/001-ground-truth-data-types.md for detailed rationale.
"""

from pathlib import Path
import pandas as pd
import logging
import re
from decimal import Decimal
from typing import List, Dict, Optional, Any, Tuple
import os
import time
import decimal

from .exceptions import GroundTruthError, DataValidationError


class GroundTruthManager:
    """Manages and validates ground truth data for invoice OCR evaluation.
    
    This class is responsible for ensuring ground truth data is properly
    formatted and valid for comparing against MLM OCR outputs.
    
    Attributes:
        ground_truth_file: Path to the ground truth CSV file
        required_columns: List of columns that must be present
        _ground_truth_data: Cached ground truth DataFrame
    """
    
    # Field specifications
    WORK_ORDER_PATTERN = r'^[A-Za-z0-9]{5}$'
    TOTAL_AMOUNT_PATTERN = r'^\$?[0-9,]*\.?[0-9]*$'
    
    # List of possible work order column names - first one is the standardized name
    WORK_ORDER_COLUMN_NAMES = [
        "Work Order Number",
        "Work Order Number/Numero de Orden",
        "Work Order Number/Numero de Orden"
    ]
    
    def __init__(
        self,
        ground_truth_file: Path,
        required_columns: Optional[List[str]] = None,
        cache_enabled: bool = True
    ) -> None:
        """Initialize the GroundTruthManager.
        
        Args:
            ground_truth_file: Path to the ground truth CSV file
            required_columns: List of required columns (default based on standardized column names)
            cache_enabled: Whether to cache validated data (default: True)
            
        Raises:
            DataValidationError: If the ground truth file doesn't exist
        """
        if not ground_truth_file.exists():
            raise DataValidationError(f"Ground truth file does not exist: {ground_truth_file}")
            
        self.ground_truth_file = ground_truth_file
        self.cache_enabled = cache_enabled
        self._ground_truth_data: Optional[pd.DataFrame] = None
        self._logger = logging.getLogger(__name__)
        
        # Set default required columns
        if required_columns is None:
            self.required_columns = ["Invoice", self.WORK_ORDER_COLUMN_NAMES[0], "Total"]
        else:
            self.required_columns = required_columns
        
    def _get_actual_work_order_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find the actual work order column name in the DataFrame.
        
        Args:
            df: DataFrame to search for work order column
            
        Returns:
            The actual column name if found, otherwise None
        """
        for col_name in self.WORK_ORDER_COLUMN_NAMES:
            if col_name in df.columns:
                return col_name
        return None
    
    def _clean_total_amount(self, value: Any) -> Tuple[float, str]:
        """Clean and validate a total amount value.
        
        Args:
            value: The value to clean and validate
            
        Returns:
            Tuple of (cleaned_float, formatted_string)
            
        Raises:
            ValueError: If value cannot be converted to a valid amount
        """
        if pd.isna(value):
            raise ValueError("Total amount cannot be empty")
            
        # Convert to string and clean
        str_val = str(value).strip()
        str_val = str_val.replace('$', '').replace(',', '')
        
        try:
            # Convert to Decimal for precise handling
            decimal_val = Decimal(str_val)
            if decimal_val < 0:
                raise ValueError("Total amount must be positive")
                
            # Format with exactly 2 decimal places
            float_val = float(decimal_val)
            formatted = f"{float_val:.2f}"
            
            self._logger.debug(f"Cleaned total amount: {value} -> {formatted}")
            return float_val, formatted
            
        except (ValueError, decimal.InvalidOperation) as e:
            raise ValueError(f"Invalid total amount format: {value}") from e
            
    def _validate_work_order(self, value: Any) -> str:
        """Validate and format a work order number.
        
        Args:
            value: The work order number to validate
            
        Returns:
            Validated work order number as string
            
        Raises:
            ValueError: If value is not a valid work order number
        """
        if pd.isna(value):
            raise ValueError("Work order number cannot be empty")
            
        str_val = str(value).strip()
        if not re.match(self.WORK_ORDER_PATTERN, str_val):
            raise ValueError(
                f"Invalid work order format: {value}. "
                "Must be exactly 5 alphanumeric characters."
            )
            
        self._logger.debug(f"Validated work order: {value}")
        return str_val
        
    def get_expected_fields(self) -> set:
        """Get the set of expected fields for extraction.
        
        Returns:
            Set of field names that should be extracted from invoices.
        """
        # Return the key fields that should be extracted from invoices
        return {"Work Order Number", "Total"}
        
    def validate_ground_truth(self) -> None:
        """Validate the structure and content of ground truth data.
        
        This method checks that:
        1. All required columns are present (with column name flexibility)
        2. No missing values in required fields
        3. Invoice IDs are unique
        4. Field values match required formats
        
        Raises:
            GroundTruthError: If validation fails
        """
        try:
            df = pd.read_csv(self.ground_truth_file)
        except Exception as e:
            raise GroundTruthError(f"Failed to read ground truth file: {str(e)}") from e
            
        # Try to find the work order column if it has a different name
        actual_work_order_col = self._get_actual_work_order_column(df)
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
        missing_cols = set(actual_required_columns) - set(df.columns)
        if missing_cols:
            raise GroundTruthError(f"Missing required columns: {missing_cols}")
            
        # Check for missing values in required columns
        missing_values = df[actual_required_columns].isnull().any()
        if missing_values.any():
            problem_cols = missing_values[missing_values].index.tolist()
            raise GroundTruthError(f"Missing values in required columns: {problem_cols}")
            
        # Check for unique invoice IDs
        if df["Invoice"].duplicated().any():
            dupes = df[df["Invoice"].duplicated()]["Invoice"].tolist()
            raise GroundTruthError(f"Duplicate invoice IDs found: {dupes}")
            
        # Validate field formats
        validation_errors = []
        
        # Create new columns for cleaned/validated data
        df['_total_float'] = None
        df['_total_formatted'] = None
        df['_work_order_validated'] = None
        
        # Get the actual work order column to use
        work_order_col = actual_work_order_col or self.WORK_ORDER_COLUMN_NAMES[0]
        
        for idx, row in df.iterrows():
            try:
                # Validate Total
                if 'Total' in df.columns:
                    float_val, formatted = self._clean_total_amount(row['Total'])
                    df.at[idx, '_total_float'] = float_val
                    df.at[idx, '_total_formatted'] = formatted
                    
                # Validate Work Order Number using the correct column name
                if work_order_col in df.columns:
                    validated = self._validate_work_order(row[work_order_col])
                    df.at[idx, '_work_order_validated'] = validated
                    
            except ValueError as e:
                validation_errors.append(f"Row {idx + 1}: {str(e)}")
                
        if validation_errors:
            raise GroundTruthError(
                "Field validation errors:\n" + "\n".join(validation_errors)
            )
            
        # Cache validated data if enabled
        if self.cache_enabled:
            self._ground_truth_data = df
            
        self._logger.info("Ground truth validation successful")
        
    def get_ground_truth(self, invoice_id: str) -> Dict[str, Any]:
        """Get the ground truth data for a specific invoice.
        
        Args:
            invoice_id: The invoice ID to get data for
            
        Returns:
            Dictionary with ground truth data and properly formatted values
            
        Raises:
            GroundTruthError: If invoice ID not found or ground truth not loaded
        """
        # Load data if not already loaded
        if self._ground_truth_data is None:
            self.validate_ground_truth()
            
        # Convert invoice_id to match DataFrame's type
        invoice_id_str = str(invoice_id)
            
        # Find the row for this invoice
        filtered = self._ground_truth_data[self._ground_truth_data["Invoice"].astype(str) == invoice_id_str]
        if len(filtered) == 0:
            raise GroundTruthError(f"Invoice ID {invoice_id} not found in ground truth data")
            
        # Get the first (should be only) matching row
        row = filtered.iloc[0]
        
        # Create result with standardized fields
        result = {}
        
        # Get the actual work order column to use
        work_order_col = self._get_actual_work_order_column(self._ground_truth_data)
        work_order_col = work_order_col or self.WORK_ORDER_COLUMN_NAMES[0]
        
        # Add fields with proper formatting
        if 'Total' in row:
            result['Total'] = row['_total_formatted']
        
        if work_order_col in row:
            # Use the standard name in the result regardless of actual column name
            result[self.WORK_ORDER_COLUMN_NAMES[0]] = row['_work_order_validated']
        
        # Add any remaining fields (except internal ones)
        for k, v in row.items():
            if k not in ['Total', self.WORK_ORDER_COLUMN_NAMES[0], '_total_float',
                         '_total_formatted', '_work_order_validated'] and not pd.isna(v):
                result[k] = v
                
        return result
        
    def clear_cache(self) -> None:
        """Clear the cached ground truth data."""
        self._ground_truth_data = None
        self._logger.debug("Cleared ground truth cache")
        
    def get_all_ground_truth(self) -> pd.DataFrame:
        """Get all ground truth data.
        
        Returns:
            DataFrame containing all ground truth data
            
        Raises:
            GroundTruthError: If ground truth not loaded
        """
        if self._ground_truth_data is None:
            self.validate_ground_truth()
            
        return self._ground_truth_data.copy()
