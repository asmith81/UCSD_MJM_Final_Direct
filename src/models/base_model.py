"""
Base interface for all model implementations.

This module defines the standard interface that all model implementations must follow.
Models are responsible for processing invoice images and extracting relevant information.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

from ..config.base_config import BaseConfig
from .model_errors import (
    ModelInitializationError,
    ModelProcessingError,
    ModelConfigError,
    ModelResourceError,
    ModelInputError,
    ModelTimeoutError
)

# Deprecated but kept for backward compatibility, use the ones from model_errors instead
class ModelInitializationError(ModelInitializationError):
    """Raised when a model fails to initialize properly."""
    pass

# Deprecated but kept for backward compatibility, use the ones from model_errors instead
class ModelProcessingError(ModelProcessingError):
    """Raised when a model fails to process an image."""
    pass


class BaseModel(ABC):
    """Abstract base class for all model implementations.
    
    This class defines the interface that all model implementations must follow.
    Models are responsible for:
    1. Initializing with configuration
    2. Processing invoice images
    3. Returning structured results
    4. Managing their own resources
    
    Implementations should:
    - Handle their own resource management
    - Implement proper error handling
    - Clean up resources when errors occur
    - Validate inputs before processing
    """
    
    @abstractmethod
    def initialize(self, config: BaseConfig) -> None:
        """Initialize the model with configuration.
        
        This method should:
        1. Validate the configuration
        2. Load model weights/resources
        3. Set up any required processing pipelines
        
        Args:
            config: Model configuration implementing BaseConfig
            
        Raises:
            ModelInitializationError: If initialization fails due to general issues
            ModelConfigError: If configuration is invalid or insufficient
            ModelResourceError: If required resources cannot be loaded or accessed
            ValueError: If configuration is invalid (deprecated, use ModelConfigError instead)
        """
        pass
        
    @abstractmethod
    def process_image(self, image_path: Path) -> Dict[str, Any]:
        """Process an invoice image and extract information.
        
        This method should:
        1. Validate the input image
        2. Preprocess the image as needed
        3. Run inference
        4. Post-process and structure the results
        
        Args:
            image_path: Path to the invoice image file
            
        Returns:
            Dict containing extracted information with standardized keys
            
        Raises:
            ModelProcessingError: If general processing fails
            ModelInputError: If the input image is invalid or corrupted
            ModelResourceError: If required resources are unavailable during processing
            ModelTimeoutError: If processing exceeds time limits
            FileNotFoundError: If image file doesn't exist
            ValueError: If image is invalid (deprecated, use ModelInputError instead)
        """
        pass
        
    @abstractmethod
    def validate_config(self, config: BaseConfig) -> bool:
        """Validate model-specific configuration.
        
        This method should verify that:
        1. All required fields are present
        2. Field values are within valid ranges
        3. Dependencies are properly specified
        
        Args:
            config: Model configuration to validate
            
        Returns:
            True if configuration is valid
            
        Raises:
            ModelConfigError: If configuration is invalid with detailed message
            ValueError: If configuration is invalid (deprecated, use ModelConfigError instead)
        """
        pass
