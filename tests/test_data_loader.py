"""Tests for the DataLoader class."""

import pytest
from pathlib import Path
import pandas as pd
from PIL import Image
import io
from unittest.mock import Mock, patch

from src.data.data_loader import DataLoader
from src.data.ground_truth_manager import GroundTruthManager
from src.data.exceptions import (
    DataLoadError,
    GroundTruthError,
    ImageLoadError,
    DataValidationError
)

# Mock data for testing
MOCK_GROUND_TRUTH_DATA = """Invoice,Work Order Number,Total,Field1,Field2
inv001,12345,123.45,value1,value2
inv002,AB123,67.89,value3,value4
"""

# Create a small test image in memory
def create_test_image():
    """Create a small test image for testing."""
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr.getvalue()

@pytest.fixture
def mock_file_system(tmp_path):
    """Create a mock file system with test data."""
    # Create directory structure
    data_dir = tmp_path / "data"
    image_dir = data_dir / "images"
    image_dir.mkdir(parents=True)
    
    # Create ground truth CSV
    ground_truth_file = data_dir / "ground_truth.csv"
    ground_truth_file.write_text(MOCK_GROUND_TRUTH_DATA)
    
    # Create test images
    test_image = create_test_image()
    (image_dir / "inv001.jpg").write_bytes(test_image)
    (image_dir / "inv002.jpg").write_bytes(test_image)
    
    return {
        "data_dir": data_dir,
        "image_dir": image_dir,
        "ground_truth_file": ground_truth_file
    }

@pytest.fixture
def mock_ground_truth_manager(mock_file_system):
    """Create a GroundTruthManager instance with mock file system."""
    return GroundTruthManager(
        ground_truth_file=mock_file_system["ground_truth_file"],
        cache_enabled=True
    )

@pytest.fixture
def data_loader(mock_file_system, mock_ground_truth_manager):
    """Create a DataLoader instance with mock file system and injected dependencies."""
    return DataLoader(
        data_dir=mock_file_system["data_dir"],
        ground_truth_manager=mock_ground_truth_manager,
        image_dir=mock_file_system["image_dir"],
        cache_enabled=True
    )

def test_data_loader_initialization(mock_file_system, mock_ground_truth_manager):
    """Test DataLoader initialization with valid paths and dependencies."""
    loader = DataLoader(
        data_dir=mock_file_system["data_dir"],
        ground_truth_manager=mock_ground_truth_manager
    )
    
    assert loader.data_dir == mock_file_system["data_dir"]
    assert loader.image_dir == mock_file_system["data_dir"] / "images"
    assert loader._ground_truth_manager == mock_ground_truth_manager
    assert loader.cache_enabled is True

def test_data_loader_initialization_custom_paths(mock_file_system, mock_ground_truth_manager):
    """Test DataLoader initialization with custom paths."""
    loader = DataLoader(
        data_dir=mock_file_system["data_dir"],
        ground_truth_manager=mock_ground_truth_manager,
        image_dir=mock_file_system["image_dir"],
        cache_enabled=False
    )
    
    assert loader.data_dir == mock_file_system["data_dir"]
    assert loader.image_dir == mock_file_system["image_dir"]
    assert loader._ground_truth_manager == mock_ground_truth_manager
    assert loader.cache_enabled is False

def test_data_loader_invalid_data_dir(tmp_path, mock_ground_truth_manager):
    """Test DataLoader initialization with invalid data directory."""
    invalid_dir = tmp_path / "nonexistent"
    
    with pytest.raises(DataValidationError) as exc_info:
        DataLoader(
            data_dir=invalid_dir,
            ground_truth_manager=mock_ground_truth_manager
        )
    assert "does not exist" in str(exc_info.value)

def test_data_loader_invalid_image_dir(mock_file_system, mock_ground_truth_manager):
    """Test DataLoader initialization with invalid image directory."""
    invalid_image_dir = mock_file_system["data_dir"] / "nonexistent"
    
    with pytest.raises(DataValidationError) as exc_info:
        DataLoader(
            data_dir=mock_file_system["data_dir"],
            ground_truth_manager=mock_ground_truth_manager,
            image_dir=invalid_image_dir
        )
    assert "does not exist" in str(exc_info.value)

def test_load_ground_truth(data_loader):
    """Test loading ground truth data."""
    df = data_loader.load_ground_truth()
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    # Check that core columns exist without checking internal validation columns
    for col in ["Invoice", "Work Order Number", "Total", "Field1", "Field2"]:
        assert col in df.columns
    assert df.iloc[0]["Invoice"] == "inv001"

def test_load_ground_truth_invalid_csv(mock_file_system):
    """Test loading invalid ground truth CSV."""
    # Write invalid CSV data with mismatched columns and corrupted format
    invalid_csv = "Invoice,Work Order Number,Total\ninv001,12345\ninv002,AB123,67.89,extra,extra2\ncompletely invalid line"
    mock_file_system["ground_truth_file"].write_text(invalid_csv)
    
    # Create ground truth manager with the invalid file
    gt_manager = GroundTruthManager(mock_file_system["ground_truth_file"])
    
    # Create loader with injected manager
    loader = DataLoader(
        data_dir=mock_file_system["data_dir"],
        ground_truth_manager=gt_manager
    )
    
    with pytest.raises(GroundTruthError):
        loader.load_ground_truth()

def test_load_image(data_loader):
    """Test loading an image."""
    image = data_loader.load_image("inv001")
    
    assert isinstance(image, Image.Image)
    assert image.size == (100, 100)
    assert image.mode == "RGB"

def test_load_nonexistent_image(data_loader):
    """Test loading a nonexistent image."""
    with pytest.raises(ImageLoadError) as exc_info:
        data_loader.load_image("nonexistent")
    assert "not found" in str(exc_info.value)

def test_load_invalid_image(mock_file_system):
    """Test loading an invalid image file."""
    # Create invalid image file
    invalid_image = mock_file_system["image_dir"] / "invalid.jpg"
    invalid_image.write_text("not an image")
    
    # Create ground truth manager
    gt_manager = GroundTruthManager(mock_file_system["ground_truth_file"])
    
    # Create loader with injected manager
    loader = DataLoader(
        data_dir=mock_file_system["data_dir"],
        ground_truth_manager=gt_manager
    )
    
    with pytest.raises(ImageLoadError):
        loader.load_image("invalid")

def test_get_available_invoice_ids(data_loader):
    """Test getting available invoice IDs."""
    ids = data_loader.get_available_invoice_ids()
    
    assert isinstance(ids, list)
    assert len(ids) == 2
    assert "inv001" in ids
    assert "inv002" in ids
    assert ids == sorted(ids)  # Check that IDs are sorted

def test_get_invoice_data(data_loader):
    """Test getting both image and ground truth for an invoice."""
    image, row = data_loader.get_invoice_data("inv001")
    
    assert isinstance(image, Image.Image)
    assert isinstance(row, dict)
    assert row["Invoice"] == "inv001"
    assert row["Field1"] == "value1"

def test_get_invoice_data_nonexistent(data_loader):
    """Test getting data for nonexistent invoice."""
    with pytest.raises(DataLoadError) as exc_info:
        data_loader.get_invoice_data("nonexistent")
    assert "not found" in str(exc_info.value)

def test_image_caching(data_loader):
    """Test that images are properly cached."""
    # First load should cache the image
    image1 = data_loader.load_image("inv001")
    
    # Mock the image file to be different
    with patch("PIL.Image.open") as mock_open:
        mock_image = Mock()
        mock_open.return_value = mock_image
        
        # Second load should return cached image
        image2 = data_loader.load_image("inv001")
        
        assert image2 is image1  # Should be the same object (cached)
        mock_open.assert_not_called()  # Should not try to load from disk

def test_clear_cache(data_loader):
    """Test clearing the cache."""
    # Load data into cache
    data_loader.load_ground_truth()
    data_loader.load_image("inv001")
    
    # Clear cache
    data_loader.clear_cache()
    
    # Check that cache is cleared
    assert data_loader._ground_truth_manager._ground_truth_data is None
    assert len(data_loader._loaded_images) == 0

def test_cache_disabled(mock_file_system, mock_ground_truth_manager):
    """Test behavior when cache is disabled."""
    loader = DataLoader(
        data_dir=mock_file_system["data_dir"],
        ground_truth_manager=mock_ground_truth_manager,
        cache_enabled=False
    )
    
    # First load
    image1 = loader.load_image("inv001")
    
    # Second load should give different object
    image2 = loader.load_image("inv001")
    
    assert image2 is not image1  # Should be different objects 