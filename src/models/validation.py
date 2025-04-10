"""
Model configuration validation utilities.

This module provides validation utilities for model configurations,
including validation results, validators, and composite validation.
"""
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

from .model_errors import ModelConfigError
from ..config.base_config import BaseConfig


class ValidationResult:
    """
    Represents the result of a validation operation.
    
    Attributes:
        is_valid: Whether the validation passed
        errors: List of error messages if validation failed
    """
    
    def __init__(self, is_valid: bool, errors: Optional[List[str]] = None):
        """
        Initialize validation result.
        
        Args:
            is_valid: Whether validation passed
            errors: Optional list of error messages
        """
        self.is_valid = is_valid
        self.errors = errors or []
    
    def __str__(self) -> str:
        """Format validation result as string."""
        if self.is_valid:
            return "Validation successful"
        
        if not self.errors:
            return "Validation failed"
            
        if len(self.errors) == 1:
            return f"Validation failed: {self.errors[0]}"
            
        error_list = "\n  - " + "\n  - ".join(self.errors)
        return f"Validation failed with multiple errors:{error_list}"


class BaseValidator(ABC):
    """Base class for all validators."""
    
    @abstractmethod
    def validate(self, config: BaseConfig) -> ValidationResult:
        """
        Validate the configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            ValidationResult indicating success/failure and any errors
        """
        pass


class ModelConfigValidator(BaseValidator):
    """Validator for model configurations."""
    
    def validate(self, config: BaseConfig) -> ValidationResult:
        """
        Validate model configuration.
        
        Args:
            config: Model configuration to validate
            
        Returns:
            ValidationResult with validation outcome
        """
        errors = []
        
        # Check basic structure
        if not config:
            return ValidationResult(False, ["Configuration is empty"])
            
        # Validate required fields
        required_fields = ["name", "type", "parameters"]
        for field in required_fields:
            if not config.has_value(field):
                errors.append(f"Missing required field: {field}")
                
        # Validate field values if present
        if config.has_value("name"):
            name = config.get_value("name")
            if not name or (isinstance(name, str) and not name.strip()):
                errors.append("Model name cannot be empty")
                
        if config.has_value("type"):
            model_type = config.get_value("type")
            if not model_type or (isinstance(model_type, str) and not model_type.strip()):
                errors.append("Model type cannot be empty")
                
        if config.has_value("parameters"):
            params = config.get_value("parameters")
            if not isinstance(params, dict):
                errors.append("Parameters must be a dictionary")
                
        return ValidationResult(len(errors) == 0, errors)


class CompositeValidator(BaseValidator):
    """Combines multiple validators into a single validator."""
    
    def __init__(self, validators: List[BaseValidator]):
        """
        Initialize with list of validators.
        
        Args:
            validators: List of validators to use
        """
        self.validators = validators
    
    def validate(self, config: BaseConfig) -> ValidationResult:
        """
        Run all validators and combine results.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Combined ValidationResult
        """
        all_errors = []
        
        for validator in self.validators:
            result = validator.validate(config)
            if not result.is_valid:
                all_errors.extend(result.errors)
                
        return ValidationResult(len(all_errors) == 0, all_errors) 