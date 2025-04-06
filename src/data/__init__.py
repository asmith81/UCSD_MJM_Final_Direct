"""Data loading and management components.

This package provides components for loading and managing invoice images
and their corresponding ground truth data.
"""

from .base_data_loader import BaseDataLoader
from .data_loader import DataLoader
from .data_loader_factory import DataLoaderFactory
from .ground_truth_manager import GroundTruthManager
from .exceptions import (
    DataLoadError,
    GroundTruthError,
    ImageLoadError,
    DataValidationError
)

# Import validation utilities
from .validation_utils import (
    validate_directory_exists,
    validate_file_exists,
    validate_csv_file,
    validate_image_directory,
    get_data_statistics,
    validate_extracted_fields
)

# Import validators
from .validators import (
    BaseValidator,
    GroundTruthValidator,
    ImageValidator, 
    ExtractedDataValidator,
    validate_total_amount,
    validate_work_order,
    normalize_total_amount,
    normalize_work_order,
    compare_extracted_to_ground_truth
)

__all__ = [
    'BaseDataLoader',
    'DataLoader',
    'DataLoaderFactory',
    'GroundTruthManager',
    'DataLoadError',
    'GroundTruthError',
    'ImageLoadError',
    'DataValidationError',
    
    # Validation utilities
    'validate_directory_exists',
    'validate_file_exists',
    'validate_csv_file',
    'validate_image_directory',
    'get_data_statistics',
    'validate_extracted_fields',
    
    # Validators
    'BaseValidator',
    'GroundTruthValidator',
    'ImageValidator',
    'ExtractedDataValidator',
    'validate_total_amount',
    'validate_work_order',
    'normalize_total_amount',
    'normalize_work_order',
    'compare_extracted_to_ground_truth'
]
