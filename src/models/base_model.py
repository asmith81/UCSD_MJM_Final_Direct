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

class BaseModel(ABC):
    """Abstract base class for all model implementations.
    
    This class defines the interface that all model implementations must follow.
    It provides a standard contract for model initialization and image processing.
    
    All implementations must properly handle:
    - Resource management (loading/unloading)
    - Error recovery and cleanup
    - Timeouts for operations
    - Input validation
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
        """
        pass
