"""Integration tests for the ImageProcessor component."""

import pytest
from pathlib import Path
import numpy as np
from PIL import Image
from typing import List

from src.config.base_config import BaseConfig
from src.image.image_processor import ImageProcessor
from src.image.image_processor_factory import ImageProcessorFactory
from src.data.data_loader import DataLoader
from src.data.ground_truth_manager import GroundTruthManager

class TestConfig(BaseConfig):
    """Test configuration implementation."""
    
    def __init__(self, data):
        self._data = data
        
    def get_data(self):
        return self._data

@pytest.fixture
def processor_config():
    """Create a processor configuration."""
    return TestConfig({
        'target_size': (1024, 1365),
        'color_mode': 'RGB',
        'normalize': True,
        'maintain_aspect_ratio': True,
        'jpeg_quality': 95,
        'contrast_factor': None,
        'brightness_factor': None,
        'sharpness_factor': None
    })

@pytest.fixture
def data_loader(tmp_path):
    """Create a data loader with test data."""
    # Create test directories
    data_dir = tmp_path / "data"
    image_dir = data_dir / "images"
    image_dir.mkdir(parents=True)
    
    # Create test ground truth file
    ground_truth_file = data_dir / "ground_truth.csv"
    ground_truth_file.write_text("Invoice,Field1\n1001,test")
    
    # Create test image
    test_image = Image.new('RGB', (3000, 4000), color='red')
    test_image.save(image_dir / "1001.jpg")
    
    # Create ground truth manager
    ground_truth_manager = GroundTruthManager(ground_truth_file)
    
    # Create and return data loader
    return DataLoader(
        data_dir=data_dir,
        ground_truth_manager=ground_truth_manager,
        image_dir=image_dir
    )

def test_processor_with_data_loader(data_loader, processor_config):
    """Test image processor with data loader integration."""
    # Create processor
    factory = ImageProcessorFactory()
    processor = factory.create_processor(config=processor_config)
    
    # Load and process image
    image = data_loader.load_image("1001")
    processed = processor.preprocess_image(image)
    
    # Verify processing results
    assert isinstance(processed, Image.Image)
    assert processed.size == (1024, 1365)
    assert processed.mode == 'RGB'

def test_batch_processing_with_data_loader(data_loader, processor_config):
    """Test batch processing with data loader."""
    # Create processor
    factory = ImageProcessorFactory()
    processor = factory.create_processor(config=processor_config)
    
    # Load multiple images
    images = [
        data_loader.load_image("1001"),
        data_loader.load_image("1001").copy()  # Use copy for testing
    ]
    
    # Process batch
    results = processor.batch_preprocess(images)
    
    # Verify results
    assert len(results) == 2
    for result in results:
        assert isinstance(result, Image.Image)
        assert result.size == (1024, 1365)
        assert result.mode == 'RGB'

def test_processor_factory_integration(processor_config):
    """Test image processor factory integration."""
    factory = ImageProcessorFactory()
    
    # Create with default type
    processor1 = factory.create_processor(config=processor_config)
    assert isinstance(processor1, ImageProcessor)
    assert processor1._initialized
    
    # Create without config
    processor2 = factory.create_processor()
    assert isinstance(processor2, ImageProcessor)
    assert not processor2._initialized
    
    # Test registration
    class CustomProcessor(ImageProcessor):
        pass
    
    factory.register_processor("custom", CustomProcessor)
    processor3 = factory.create_processor("custom", processor_config)
    assert isinstance(processor3, CustomProcessor)

def test_memory_usage(data_loader, processor_config):
    """Test memory usage during processing."""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Create and use processor
    factory = ImageProcessorFactory()
    processor = factory.create_processor(config=processor_config)
    
    # Process multiple images
    images = [data_loader.load_image("1001") for _ in range(5)]
    results = processor.batch_preprocess(images)
    
    # Check memory usage
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Memory increase should be reasonable (less than 1GB)
    assert memory_increase < 1024 * 1024 * 1024  # 1GB in bytes

def test_processing_performance(data_loader, processor_config):
    """Test processing performance."""
    import time
    
    factory = ImageProcessorFactory()
    processor = factory.create_processor(config=processor_config)
    
    # Time single image processing
    image = data_loader.load_image("1001")
    
    start_time = time.time()
    processor.preprocess_image(image)
    single_time = time.time() - start_time
    
    # Time batch processing
    images = [image.copy() for _ in range(5)]
    
    start_time = time.time()
    processor.batch_preprocess(images)
    batch_time = time.time() - start_time
    
    # Batch processing should be more efficient than individual processing
    assert batch_time < single_time * len(images)

def test_image_quality_preservation(data_loader, processor_config):
    """Test that important image features are preserved."""
    factory = ImageProcessorFactory()
    processor = factory.create_processor(config=processor_config)
    
    # Create test image with specific features
    size = (3000, 4000)
    image = Image.new('RGB', size)
    
    # Add some test patterns
    pixels = np.array(image)
    pixels[1000:2000, 1000:2000] = [255, 0, 0]  # Red square
    pixels[2000:2500, 2000:2500] = [0, 255, 0]  # Green square
    image = Image.fromarray(pixels)
    
    # Process image
    processed = processor.preprocess_image(image)
    
    # Verify feature preservation
    processed_pixels = np.array(processed)
    
    # Check if color regions are still distinct
    assert np.any(processed_pixels[:, :, 0] > processed_pixels[:, :, 1])  # Red present
    assert np.any(processed_pixels[:, :, 1] > processed_pixels[:, :, 0])  # Green present 