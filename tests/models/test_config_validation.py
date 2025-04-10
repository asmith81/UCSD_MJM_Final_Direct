"""
Tests for model configuration validation utilities.

This module contains comprehensive tests for the configuration validation system,
including composite validators, validation results, and lifecycle integration.
"""
import pytest
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch
from PIL import Image

from src.config.base_config import BaseConfig
from src.models.base_model import BaseModel
from src.models.base_model_impl import BaseModelImpl
from src.models.model_errors import ModelConfigError
from src.models.validation import (
    ValidationResult,
    ModelConfigValidator,
    CompositeValidator,
    BaseValidator
)

class MockValidator(BaseValidator):
    """Mock validator for testing."""
    def __init__(self, should_pass: bool = True, error_message: str = "Validation failed"):
        self.should_pass = should_pass
        self.error_message = error_message
        self.validate_called = False
        
    def validate(self, config: BaseConfig) -> ValidationResult:
        """Mock validation that returns configurable result."""
        self.validate_called = True
        if self.should_pass:
            return ValidationResult(True)
        return ValidationResult(False, [self.error_message])

class MockConfig(BaseConfig):
    """Mock configuration for testing."""
    def __init__(self, data: Dict[str, Any]):
        self._data = data
        
    def get_data(self) -> Dict[str, Any]:
        return self._data
        
    def get_value(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)
        
    def validate(self) -> bool:
        return True
        
    def get_section(self, section: str) -> Dict[str, Any]:
        return self._data.get(section, {})
        
    def has_value(self, key: str) -> bool:
        """Check if a key exists in the configuration."""
        return key in self._data

def test_composite_validator_chaining():
    """Test chaining multiple validators together."""
    # Create validators with different behaviors
    pass_validator = MockValidator(True)
    fail_validator = MockValidator(False, "Validation 1 failed")
    another_fail = MockValidator(False, "Validation 2 failed")
    
    # Test all passing
    composite = CompositeValidator([MockValidator(True), MockValidator(True)])
    config = MockConfig({"test": "data"})
    result = composite.validate(config)
    assert result.is_valid
    assert not result.errors
    
    # Test one failing
    composite = CompositeValidator([pass_validator, fail_validator])
    result = composite.validate(config)
    assert not result.is_valid
    assert len(result.errors) == 1
    assert "Validation 1 failed" in result.errors
    
    # Test multiple failing
    composite = CompositeValidator([fail_validator, another_fail])
    result = composite.validate(config)
    assert not result.is_valid
    assert len(result.errors) == 2
    assert "Validation 1 failed" in result.errors
    assert "Validation 2 failed" in result.errors

def test_composite_validator_result_aggregation():
    """Test aggregation of validation results from multiple validators."""
    # Create validators with different error messages
    validators = [
        MockValidator(False, "Error in field 1"),
        MockValidator(False, "Error in field 2"),
        MockValidator(True),
        MockValidator(False, "Error in field 3")
    ]
    
    composite = CompositeValidator(validators)
    config = MockConfig({"test": "data"})
    result = composite.validate(config)
    
    # Check result aggregation
    assert not result.is_valid
    assert len(result.errors) == 3
    assert "Error in field 1" in result.errors
    assert "Error in field 2" in result.errors
    assert "Error in field 3" in result.errors
    
    # Verify all validators were called
    assert all(v.validate_called for v in validators)

def test_nested_config_validation():
    """Test validation of nested configuration structures."""
    config_data = {
        "name": "test_model",
        "type": "test",
        "parameters": {
            "nested": {
                "field1": 123,
                "field2": "value"
            },
            "array_param": [1, 2, 3]
        }
    }
    
    class NestedValidator(BaseValidator):
        def validate(self, config: BaseConfig) -> ValidationResult:
            params = config.get_value("parameters", {})
            nested = params.get("nested", {})
            
            errors = []
            if not isinstance(nested.get("field1"), int):
                errors.append("field1 must be an integer")
            if not isinstance(nested.get("field2"), str):
                errors.append("field2 must be a string")
                
            return ValidationResult(len(errors) == 0, errors)
    
    # Test valid nested config
    config = MockConfig(config_data)
    validator = NestedValidator()
    result = validator.validate(config)
    assert result.is_valid
    assert not result.errors
    
    # Test invalid nested config
    invalid_config = MockConfig({
        "parameters": {
            "nested": {
                "field1": "not an int",
                "field2": 123
            }
        }
    })
    result = validator.validate(invalid_config)
    assert not result.is_valid
    assert len(result.errors) == 2
    assert "field1 must be an integer" in result.errors
    assert "field2 must be a string" in result.errors

def test_array_config_validation():
    """Test validation of array/list type configuration values."""
    class ArrayValidator(BaseValidator):
        def validate(self, config: BaseConfig) -> ValidationResult:
            params = config.get_value("parameters", {})
            array_param = params.get("array_param", [])
            
            errors = []
            if not isinstance(array_param, list):
                errors.append("array_param must be a list")
            elif not all(isinstance(x, int) for x in array_param):
                errors.append("all array_param elements must be integers")
            elif len(array_param) < 1:
                errors.append("array_param must not be empty")
                
            return ValidationResult(len(errors) == 0, errors)
    
    # Test valid array config
    config = MockConfig({
        "parameters": {
            "array_param": [1, 2, 3]
        }
    })
    validator = ArrayValidator()
    result = validator.validate(config)
    assert result.is_valid
    assert not result.errors
    
    # Test invalid array configs
    invalid_configs = [
        ({"parameters": {"array_param": "not a list"}}, "array_param must be a list"),
        ({"parameters": {"array_param": [1, "2", 3]}}, "all array_param elements must be integers"),
        ({"parameters": {"array_param": []}}, "array_param must not be empty")
    ]
    
    for config_data, expected_error in invalid_configs:
        result = validator.validate(MockConfig(config_data))
        assert not result.is_valid
        assert expected_error in result.errors

def test_validation_result_formatting():
    """Test validation result error message formatting."""
    # Test single error
    result = ValidationResult(False, ["Single error message"])
    assert str(result) == "Validation failed: Single error message"
    
    # Test multiple errors
    result = ValidationResult(False, ["Error 1", "Error 2", "Error 3"])
    result_str = str(result)
    assert "Validation failed" in result_str
    assert "Error 1" in result_str
    assert "Error 2" in result_str
    assert "Error 3" in result_str
    
    # Test successful validation
    result = ValidationResult(True)
    assert str(result) == "Validation successful"
    
    # Test empty error list
    result = ValidationResult(False, [])
    assert str(result) == "Validation failed"

class TestValidationLifecycle:
    """Test validation lifecycle integration with BaseModelImpl."""
    
    class TestModel(BaseModelImpl):
        def __init__(self):
            """Initialize the test model."""
            super().__init__()
            self.initialized = False
            
        def _initialize_impl(self, config: BaseConfig) -> bool:
            self.initialized = True
            return True
            
        def _process_image_impl(self, image: Image.Image, image_path: Path) -> Dict[str, Any]:
            return {"result": "test"}
            
        def _validate_config_impl(self, config: BaseConfig) -> ValidationResult:
            if not hasattr(config, "required_field"):
                return ValidationResult(False, ["Missing required field"])
            return ValidationResult(True, [])
    
    @pytest.fixture
    def model(self):
        return self.TestModel()
    
    def test_validation_lifecycle_hooks(self, model):
        """Test validation hooks in model lifecycle."""
        # Test validation during initialization
        valid_config = MockConfig({"required_field": "value"})
        model.initialize(valid_config)
        assert model.initialized
        
        # Test validation failure during initialization
        invalid_config = MockConfig({})
        with pytest.raises(ModelConfigError) as exc_info:
            model.initialize(invalid_config)
        assert "Missing required field" in str(exc_info.value)
        assert not model.initialized
        
        # Test validation with composite validator
        validator1 = MockValidator(True)
        validator2 = MockValidator(True)
        composite = CompositeValidator([validator1, validator2])
        
        with patch.object(model, '_validate_config_impl', return_value=True):
            model.initialize(valid_config)
            assert model.initialized
            assert validator1.validate_called
            assert validator2.validate_called 