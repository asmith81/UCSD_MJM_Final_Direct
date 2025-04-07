"""
Test the model error hierarchy.

This module tests the model error hierarchy to ensure
proper error creation, inheritance, and message formatting.
"""
import pytest
from src.models.model_errors import (
    ModelError,
    ModelInitializationError,
    ModelConfigError,
    ModelResourceError,
    ModelProcessingError,
    ModelInputError,
    ModelTimeoutError
)


class TestModelErrors:
    """Test the model error hierarchy and error message formatting."""
    
    def test_base_model_error(self):
        """Test base ModelError creation."""
        # Basic error
        error = ModelError("Test error")
        assert str(error) == "Test error"
        assert error.model_name is None
        
        # Error with model name
        error = ModelError("Test error", model_name="test_model")
        assert str(error) == "[test_model] Test error"
        assert error.model_name == "test_model"
    
    def test_model_initialization_error(self):
        """Test ModelInitializationError creation and formatting."""
        # Basic initialization error
        error = ModelInitializationError("Failed to initialize")
        assert "Initialization failed: Failed to initialize" in str(error)
        assert error.component is None
        
        # With model name
        error = ModelInitializationError(
            "Failed to initialize", 
            model_name="test_model"
        )
        assert "[test_model]" in str(error)
        
        # With component
        error = ModelInitializationError(
            "Failed to initialize", 
            component="weights_loader"
        )
        assert "in component 'weights_loader'" in str(error)
        assert error.component == "weights_loader"
        
        # With model name and component
        error = ModelInitializationError(
            "Failed to initialize", 
            model_name="test_model",
            component="weights_loader"
        )
        assert "[test_model] Initialization failed in component 'weights_loader': Failed to initialize" == str(error)
    
    def test_model_config_error(self):
        """Test ModelConfigError creation and formatting."""
        # Basic config error
        error = ModelConfigError("Invalid configuration")
        assert str(error) == "Invalid configuration"
        assert error.parameter is None
        
        # With parameter
        error = ModelConfigError(
            "Must be positive",
            parameter="batch_size"
        )
        assert "Invalid configuration parameter 'batch_size': Must be positive" in str(error)
        assert error.parameter == "batch_size"
        
        # With parameter and value
        error = ModelConfigError(
            "Must be positive",
            parameter="batch_size",
            value=-1
        )
        assert "Invalid configuration parameter 'batch_size': Must be positive. Got '-1'" in str(error)
        assert error.value == -1
        
        # With parameter, value, and expected
        error = ModelConfigError(
            "Must be positive",
            parameter="batch_size",
            value=-1,
            expected="positive integer"
        )
        assert "Invalid configuration parameter 'batch_size': Must be positive. Got '-1', expected positive integer" in str(error)
        assert error.expected == "positive integer"
        
        # With model name
        error = ModelConfigError(
            "Invalid configuration",
            model_name="test_model"
        )
        assert "[test_model]" in str(error)
    
    def test_model_resource_error(self):
        """Test ModelResourceError creation and formatting."""
        # Basic resource error
        error = ModelResourceError("Resource error")
        assert "Resource error: Resource error" in str(error)
        assert error.resource_type is None
        assert error.resource_name is None
        
        # With resource type
        error = ModelResourceError(
            "Not found",
            resource_type="model_weights"
        )
        assert "Resource error for model_weights: Not found" in str(error)
        assert error.resource_type == "model_weights"
        
        # With resource name
        error = ModelResourceError(
            "Not found",
            resource_name="model.pt"
        )
        assert "Resource error for 'model.pt': Not found" in str(error)
        assert error.resource_name == "model.pt"
        
        # With resource type and name
        error = ModelResourceError(
            "Not found",
            resource_type="model_weights",
            resource_name="model.pt"
        )
        assert "Resource error for model_weights 'model.pt': Not found" in str(error)
        
        # With model name
        error = ModelResourceError(
            "Resource error",
            model_name="test_model"
        )
        assert "[test_model]" in str(error)
    
    def test_model_processing_error(self):
        """Test ModelProcessingError creation and formatting."""
        # Basic processing error
        error = ModelProcessingError("Processing failed")
        assert "Processing failed: Processing failed" in str(error)
        assert error.image_path is None
        assert error.processing_stage is None
        
        # With image path
        error = ModelProcessingError(
            "Invalid format",
            image_path="test.jpg"
        )
        assert "Processing failed image 'test.jpg': Invalid format" in str(error)
        assert error.image_path == "test.jpg"
        
        # With processing stage
        error = ModelProcessingError(
            "Out of memory",
            processing_stage="inference"
        )
        assert "Processing failed during inference: Out of memory" in str(error)
        assert error.processing_stage == "inference"
        
        # With image path and processing stage
        error = ModelProcessingError(
            "Out of memory",
            image_path="test.jpg",
            processing_stage="inference"
        )
        assert "Processing failed image 'test.jpg', during inference: Out of memory" in str(error)
        
        # With model name
        error = ModelProcessingError(
            "Processing failed",
            model_name="test_model"
        )
        assert "[test_model]" in str(error)
    
    def test_model_input_error(self):
        """Test ModelInputError creation and formatting."""
        # Basic input error
        error = ModelInputError("Invalid input")
        assert str(error) == "Invalid input"
        assert error.input_name is None
        
        # With input name
        error = ModelInputError(
            "Must be an image",
            input_name="document"
        )
        assert "Invalid input 'document': Must be an image" in str(error)
        assert error.input_name == "document"
        
        # With input name and value
        error = ModelInputError(
            "Must be an image",
            input_name="document",
            input_value="text.txt"
        )
        assert "Invalid input 'document': Must be an image. Got 'text.txt'" in str(error)
        assert error.input_value == "text.txt"
        
        # With input name, value, and expected
        error = ModelInputError(
            "Must be an image",
            input_name="document",
            input_value="text.txt",
            expected="jpg, png, or pdf"
        )
        assert "Invalid input 'document': Must be an image. Got 'text.txt', expected jpg, png, or pdf" in str(error)
        assert error.expected == "jpg, png, or pdf"
        
        # With model name
        error = ModelInputError(
            "Invalid input",
            model_name="test_model"
        )
        assert "[test_model]" in str(error)
    
    def test_model_timeout_error(self):
        """Test ModelTimeoutError creation and formatting."""
        # Basic timeout error
        error = ModelTimeoutError("Processing timed out")
        assert "Timeout: Processing timed out" in str(error)
        assert error.timeout_seconds is None
        
        # With timeout seconds
        error = ModelTimeoutError(
            "Processing timed out",
            timeout_seconds=30.5
        )
        assert "Timeout after 30.5s: Processing timed out" in str(error)
        assert error.timeout_seconds == 30.5
        
        # With image path
        error = ModelTimeoutError(
            "Processing timed out",
            image_path="test.jpg"
        )
        assert "image 'test.jpg'" in str(error)
        assert error.image_path == "test.jpg"
        
        # With model name
        error = ModelTimeoutError(
            "Processing timed out",
            model_name="test_model"
        )
        assert "[test_model]" in str(error)
        
        # With all fields
        error = ModelTimeoutError(
            "Processing timed out",
            model_name="test_model",
            image_path="test.jpg",
            timeout_seconds=30.5
        )
        # ModelTimeoutError inherits from ModelProcessingError and adds "inference" as processing_stage
        # So we should verify that the expected components are in the string rather than requiring an exact match
        assert "[test_model]" in str(error) 
        assert "Processing failed" in str(error)
        assert "image 'test.jpg'" in str(error)
        assert "during inference" in str(error)
        assert "Timeout after 30.5s" in str(error)
        assert "Processing timed out" in str(error) 