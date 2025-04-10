"""
Tests for the BaseModel interface and implementations.

This module contains both unit tests for the interface requirements
and integration tests using a mock implementation.
"""

import pytest
from pathlib import Path
from typing import Dict, Any

from src.config.base_config import BaseConfig
from src.models.base_model import BaseModel
from src.models.model_errors import (
    ModelInitializationError,
    ModelProcessingError,
    ModelConfigError,
    ModelInputError
)


class MockConfig(BaseConfig):
    """Mock configuration for testing."""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data

    def validate(self) -> bool:
        return True

    def get_data(self) -> Dict[str, Any]:
        return self.data

    def get_value(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def get_section(self, section: str) -> Dict[str, Any]:
        return self.data.get(section, {})


class MockModel(BaseModel):
    """Mock model implementation for testing."""
    
    def __init__(self):
        self.initialized = False
        self.config = None

    def initialize(self, config: BaseConfig) -> None:
        if not self.validate_config(config):
            raise ValueError("Invalid configuration")
        self.config = config
        self.initialized = True

    def process_image(self, image_path: Path) -> Dict[str, Any]:
        if not self.initialized:
            raise ModelInitializationError("Model not initialized")
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        # Mock processing result
        return {"status": "success", "text": "mock extraction"}

    def validate_config(self, config: BaseConfig) -> bool:
        required_fields = ["model_type", "version"]
        for field in required_fields:
            if not config.get_value(field):
                raise ValueError(f"Missing required field: {field}")
        return True


# Unit Tests

def test_model_interface_definition():
    """Test that BaseModel defines required abstract methods."""
    # Verify abstract methods exist
    assert hasattr(BaseModel, "initialize")
    assert hasattr(BaseModel, "process_image")
    assert hasattr(BaseModel, "validate_config")


def test_custom_exceptions():
    """Test that custom exceptions are properly defined."""
    assert issubclass(ModelInitializationError, Exception)
    assert issubclass(ModelProcessingError, Exception)


# Integration Tests

@pytest.fixture
def mock_model():
    """Fixture providing a mock model instance."""
    return MockModel()


@pytest.fixture
def valid_config():
    """Fixture providing a valid configuration."""
    return MockConfig({
        "model_type": "mock",
        "version": "1.0",
        "parameters": {
            "batch_size": 1
        }
    })


@pytest.fixture
def invalid_config():
    """Fixture providing an invalid configuration."""
    return MockConfig({
        "parameters": {
            "batch_size": 1
        }
    })


def test_model_initialization(mock_model, valid_config):
    """Test successful model initialization."""
    mock_model.initialize(valid_config)
    assert mock_model.initialized
    assert mock_model.config == valid_config


def test_model_initialization_invalid_config(mock_model, invalid_config):
    """Test model initialization with invalid config."""
    with pytest.raises(ModelConfigError) as exc_info:
        mock_model.initialize(invalid_config)
    assert "Missing required field" in str(exc_info.value)
    assert not mock_model.initialized


def test_process_image_without_initialization(mock_model, tmp_path):
    """Test processing image without initialization."""
    image_path = tmp_path / "test.jpg"
    image_path.touch()  # Create empty file
    
    with pytest.raises(ModelInitializationError):
        mock_model.process_image(image_path)


def test_process_image_missing_file(mock_model, valid_config, tmp_path):
    """Test processing non-existent image."""
    mock_model.initialize(valid_config)
    
    with pytest.raises(FileNotFoundError):
        mock_model.process_image(tmp_path / "nonexistent.jpg")


def test_successful_image_processing(mock_model, valid_config, tmp_path):
    """Test successful image processing."""
    # Setup
    mock_model.initialize(valid_config)
    image_path = tmp_path / "test.jpg"
    image_path.touch()  # Create empty file
    
    # Process
    result = mock_model.process_image(image_path)
    
    # Verify
    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert "text" in result 