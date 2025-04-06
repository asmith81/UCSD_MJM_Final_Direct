"""Tests for the ImageProcessor class."""

import pytest
import numpy as np
from PIL import Image
from dataclasses import dataclass
from typing import Dict, Any

from src.image.image_processor import ImageProcessor
from src.image.exceptions import ImageProcessingError, ImageValidationError, ConfigurationError

@dataclass
class MockConfig:
    """Mock configuration for testing."""
    _data: Dict[str, Any]
    
    def get_data(self) -> Dict[str, Any]:
        return self._data

@pytest.fixture
def valid_config():
    """Create a valid configuration for testing."""
    return MockConfig({
        'target_size': (100, 100),
        'color_mode': 'RGB',
        'normalize': True,
        'maintain_aspect_ratio': True,
        'jpeg_quality': 95,
        'contrast_factor': None,
        'brightness_factor': None,
        'sharpness_factor': None
    })

@pytest.fixture
def test_image():
    """Create a test image for testing."""
    return Image.new('RGB', (200, 200), color='red')

def test_initialization():
    """Test processor initialization."""
    processor = ImageProcessor()
    assert not processor._initialized
    
    config = MockConfig({
        'target_size': (100, 100),
        'color_mode': 'RGB',
        'normalize': True,
        'maintain_aspect_ratio': True
    })
    
    processor.initialize(config)
    assert processor._initialized
    assert processor.config == config

def test_initialization_with_invalid_config():
    """Test initialization with invalid configuration."""
    processor = ImageProcessor()
    
    # Missing required field
    invalid_config = MockConfig({
        'color_mode': 'RGB',
        'normalize': True
    })
    
    with pytest.raises(ConfigurationError):
        processor.initialize(invalid_config)

def test_validate_image(test_image):
    """Test image validation."""
    processor = ImageProcessor()
    
    # Valid image
    assert processor.validate_image(test_image)
    
    # Invalid input
    assert not processor.validate_image("not an image")
    assert not processor.validate_image(None)

def test_preprocess_image(test_image, valid_config):
    """Test image preprocessing."""
    processor = ImageProcessor()
    processor.initialize(valid_config)
    
    # Process valid image
    result = processor.preprocess_image(test_image)
    assert isinstance(result, Image.Image)
    assert result.size == (100, 100)
    assert result.mode == 'RGB'

def test_preprocess_image_without_initialization(test_image):
    """Test preprocessing without initialization."""
    processor = ImageProcessor()
    
    with pytest.raises(ImageProcessingError):
        processor.preprocess_image(test_image)

def test_preprocess_image_with_invalid_image(valid_config):
    """Test preprocessing with invalid image."""
    processor = ImageProcessor()
    processor.initialize(valid_config)
    
    with pytest.raises(ImageValidationError):
        processor.preprocess_image("not an image")

def test_batch_preprocess(test_image, valid_config):
    """Test batch preprocessing."""
    processor = ImageProcessor()
    processor.initialize(valid_config)
    
    # Process batch of images
    images = [test_image, test_image.copy()]
    results = processor.batch_preprocess(images)
    
    assert len(results) == 2
    for result in results:
        assert isinstance(result, Image.Image)
        assert result.size == (100, 100)
        assert result.mode == 'RGB'

def test_batch_preprocess_with_errors(test_image, valid_config):
    """Test batch preprocessing with some invalid images."""
    processor = ImageProcessor()
    processor.initialize(valid_config)
    
    # Mix of valid and invalid images
    images = [test_image, "not an image", test_image.copy()]
    
    with pytest.raises(ImageProcessingError) as exc_info:
        processor.batch_preprocess(images)
    assert "Batch processing failed" in str(exc_info.value)

def test_resize_with_aspect_ratio(test_image, valid_config):
    """Test image resizing with aspect ratio preservation."""
    processor = ImageProcessor()
    processor.initialize(valid_config)
    
    # Create rectangular image
    rect_image = Image.new('RGB', (400, 200), color='red')
    
    # Resize with aspect ratio
    result = processor._resize_image(rect_image, (100, 100), True)
    
    # Should maintain aspect ratio
    assert result.size[0] / result.size[1] == rect_image.size[0] / rect_image.size[1]

def test_normalize_image(test_image):
    """Test image normalization."""
    processor = ImageProcessor()
    
    # Create test image with known values
    data = np.full((100, 100, 3), 128, dtype=np.uint8)
    test_image = Image.fromarray(data)
    
    # Normalize
    result = processor._normalize_image(test_image)
    
    # Check values are normalized
    result_array = np.array(result)
    assert result_array.max() <= 255
    assert result_array.min() >= 0

def test_apply_enhancements(test_image):
    """Test image enhancement application."""
    processor = ImageProcessor()
    
    # Test with all enhancements
    config_data = {
        'contrast_factor': 1.2,
        'brightness_factor': 1.1,
        'sharpness_factor': 1.3
    }
    
    result = processor._apply_enhancements(test_image, config_data)
    assert isinstance(result, Image.Image)
    
    # Test with no enhancements
    config_data = {
        'contrast_factor': None,
        'brightness_factor': None,
        'sharpness_factor': None
    }
    
    result = processor._apply_enhancements(test_image, config_data)
    assert isinstance(result, Image.Image) 