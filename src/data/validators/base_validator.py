"""Base validator interface.

This module defines the base interface for all validators in the system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple


class BaseValidator(ABC):
    """Base interface for all validators.
    
    This abstract base class defines the standard interface that all validators
    must implement, ensuring consistent validation behavior across the system.
    
    Attributes:
        validation_errors: List of validation errors found
        strict_mode: Whether validation should fail on any error
    """
    
    def __init__(self, strict_mode: bool = True) -> None:
        """Initialize the validator.
        
        Args:
            strict_mode: Whether to use strict validation (default: True)
        """
        self.validation_errors: List[str] = []
        self.strict_mode = strict_mode
        
    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Validate the provided data.
        
        Args:
            data: The data to validate
            
        Returns:
            True if validation passes, False otherwise
        """
        pass
        
    def add_error(self, error_message: str) -> None:
        """Add a validation error message.
        
        Args:
            error_message: The error message to add
        """
        self.validation_errors.append(error_message)
        
    def get_errors(self) -> List[str]:
        """Get all validation error messages.
        
        Returns:
            List of error messages
        """
        return self.validation_errors
        
    def clear_errors(self) -> None:
        """Clear all validation error messages."""
        self.validation_errors = []
        
    def has_errors(self) -> bool:
        """Check if there are any validation errors.
        
        Returns:
            True if there are errors, False otherwise
        """
        return len(self.validation_errors) > 0
        
    def get_validation_report(self) -> Dict[str, Any]:
        """Get a comprehensive validation report.
        
        Returns:
            Dictionary containing validation results and statistics
        """
        return {
            "valid": not self.has_errors(),
            "strict_mode": self.strict_mode,
            "error_count": len(self.validation_errors),
            "errors": self.validation_errors
        } 