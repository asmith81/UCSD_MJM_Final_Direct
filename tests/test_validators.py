import os
import tempfile
import pytest
import pandas as pd
from pathlib import Path
from PIL import Image

from src.data.validators.base_validator import BaseValidator
from src.data.validators.field_validators import (
    validate_total_amount,
    validate_work_order
)
from src.data.validators.extracted_data_validator import ExtractedDataValidator
from src.data.validators.ground_truth_validator import GroundTruthValidator
from src.data.validators.image_validator import ImageValidator


class MockValidator(BaseValidator):
    """Mock implementation of BaseValidator for testing."""
    
    def validate(self, data):
        """Simple implementation that checks if data is a dict."""
        if not isinstance(data, dict):
            self.add_error("Data must be a dictionary")
            return False
        return True


class TestBaseValidator:
    """Test suite for the BaseValidator abstract class."""
    
    def test_init(self):
        """Test initializing a validator."""
        validator = MockValidator()
        assert validator is not None
        
    def test_validate_abstract(self):
        """Test that the base validate method is abstract."""
        with pytest.raises(TypeError):
            BaseValidator()
            
    def test_mock_validate(self):
        """Test the validate method of MockValidator."""
        validator = MockValidator()
        
        # Valid input
        result = validator.validate({"key": "value"})
        assert result is True
        assert validator.get_errors() == []
        
        # Invalid input
        result = validator.validate("not a dict")
        assert result is False
        assert len(validator.get_errors()) > 0

        # Test get_validation_report
        report = validator.get_validation_report()
        assert report["valid"] is False
        assert report["error_count"] > 0
        assert "errors" in report


class TestExtractedDataValidator:
    """Test suite for the ExtractedDataValidator class."""
    
    @pytest.fixture
    def validator(self):
        """Create an ExtractedDataValidator instance."""
        return ExtractedDataValidator()
    
    @pytest.fixture
    def valid_extracted_data(self):
        """Create valid extracted data for testing."""
        return {
            "invoice_id": "INV-12345",
            "Total": "$123.45",
            "Work Order Number": "AB123",
            "date": "2023-04-01",
            "vendor": "Test Vendor"
        }
    
    @pytest.fixture
    def invalid_extracted_data(self):
        """Create invalid extracted data for testing."""
        return {
            "invoice_id": "INV-12345",
            "Total": "invalid",
            "Work Order Number": "invalid",
            "date": "2023-04-01"
        }
    
    def test_validate_valid_data(self, validator, valid_extracted_data):
        """Test validation with valid data."""
        result = validator.validate(valid_extracted_data)
        assert result is True
        assert validator.get_errors() == []
        
        # Get detailed field validation results
        field_results = validator.get_field_validation_results(valid_extracted_data)
        assert "Total" in field_results
        assert field_results["Total"]["valid"] is True
        assert field_results["Total"]["normalized"] is not None
        
    def test_validate_invalid_data(self, validator, invalid_extracted_data):
        """Test validation with invalid data."""
        result = validator.validate(invalid_extracted_data)
        
        # The validation should fail with errors
        assert result is False
        assert len(validator.get_errors()) > 0
        
        # Check field validation results
        field_results = validator.get_field_validation_results(invalid_extracted_data)
        assert "Total" in field_results
        assert field_results["Total"]["valid"] is False
        assert field_results["Total"]["normalized"] is None
        assert field_results["Work Order Number"]["valid"] is False
        
    def test_validate_empty_data(self, validator):
        """Test validation with empty data."""
        result = validator.validate({})
        assert result is False
        assert len(validator.get_errors()) > 0
        
        # Check validation report
        report = validator.get_validation_report()
        assert report["valid"] is False
        assert report["error_count"] > 0


class TestGroundTruthValidatorBasic:
    """Basic tests for the GroundTruthValidator class without DataFrame dependencies."""
    
    @pytest.fixture
    def validator(self):
        """Create a GroundTruthValidator instance."""
        return GroundTruthValidator()
    
    def test_init(self, validator):
        """Test initializing a ground truth validator."""
        assert validator is not None
        assert hasattr(validator, 'validate')


class TestImageValidator:
    """Test suite for the ImageValidator class."""
    
    @pytest.fixture
    def temp_test_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Clean up
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def validator(self):
        """Create an ImageValidator instance with lower size requirements for testing."""
        return ImageValidator(min_width=10, min_height=10)
    
    @pytest.fixture
    def valid_image_path(self, temp_test_dir):
        """Create a valid test image."""
        img_path = os.path.join(temp_test_dir, "valid.png")
        img = Image.new('RGB', (100, 100), color=(255, 255, 255))
        img.save(img_path)
        return img_path
    
    @pytest.fixture
    def invalid_image_path(self, temp_test_dir):
        """Create an invalid 'image' file."""
        img_path = os.path.join(temp_test_dir, "invalid.png")
        with open(img_path, 'w') as f:
            f.write("This is not a valid image file")
        return img_path
    
    @pytest.fixture
    def nonexistent_image_path(self, temp_test_dir):
        """Return a path to a nonexistent image."""
        return os.path.join(temp_test_dir, "nonexistent.png")
    
    def test_validate_valid_image(self, validator, valid_image_path):
        """Test validation with a valid image."""
        result = validator.validate(valid_image_path)
        assert result is True
        assert validator.get_errors() == []
        
        # Test get_image_info
        image_info = validator.get_image_info(valid_image_path)
        assert image_info["valid"] is True
        assert image_info["width"] == 100
        assert image_info["height"] == 100
        
    def test_validate_invalid_image(self, validator, invalid_image_path):
        """Test validation with an invalid image."""
        result = validator.validate(invalid_image_path)
        assert result is False
        assert len(validator.get_errors()) > 0
        
    def test_validate_nonexistent_image(self, validator, nonexistent_image_path):
        """Test validation with a nonexistent image."""
        result = validator.validate(nonexistent_image_path)
        assert result is False
        assert len(validator.get_errors()) > 0
        
    def test_validate_with_size_constraints(self, valid_image_path):
        """Test validation with size constraints."""
        # Create validator with size constraints
        large_size_validator = ImageValidator(
            min_width=200,  # Larger than test image
            min_height=200
        )
        
        result = large_size_validator.validate(valid_image_path)
        assert result is False
        assert len(large_size_validator.get_errors()) > 0
        assert any("width too small" in err.lower() for err in large_size_validator.get_errors())
        
        # Test with acceptable constraints
        small_size_validator = ImageValidator(
            min_width=50,  # Smaller than test image
            min_height=50
        )
        
        result = small_size_validator.validate(valid_image_path)
        assert result is True 