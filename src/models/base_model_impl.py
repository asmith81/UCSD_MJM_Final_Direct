"""
Base Model Implementation.

This module provides a base implementation of the BaseModel interface
with comprehensive error handling and resource management.
"""
import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, List

from PIL import Image

from ..config.base_config import BaseConfig
from .base_model import BaseModel
from .model_errors import (
    ModelInitializationError,
    ModelConfigError, 
    ModelProcessingError,
    ModelResourceError,
    ModelInputError,
    ModelTimeoutError
)
from .model_resource_manager import ModelResourceManager

# Set up logger for this module
logger = logging.getLogger(__name__)


class BaseModelImpl(BaseModel, ABC):
    """
    Base implementation of the BaseModel interface.
    
    This class provides common functionality for all model implementations:
    - Resource management through ModelResourceManager
    - Error handling during initialization and inference
    - Image validation and preprocessing
    - Timeouts for processing
    
    Concrete implementations should extend this class and implement
    the abstract methods.
    """
    
    def __init__(self):
        """Initialize the base model implementation."""
        self._model_name = None
        self._is_initialized = False
        self._resource_manager = None
        self._config = None
        self._timeout_seconds = 60.0  # Default timeout
        
    def initialize(self, config: BaseConfig) -> None:
        """
        Initialize the model with configuration.
        
        This method:
        1. Validates the configuration
        2. Sets up resource management
        3. Calls implementation-specific initialization
        
        Args:
            config: Model configuration
            
        Raises:
            ModelInitializationError: If initialization fails
            ModelConfigError: If configuration is invalid
            ModelResourceError: If required resources cannot be loaded
        """
        try:
            # Validate configuration
            if not self.validate_config(config):
                raise ModelConfigError(
                    "Configuration validation failed",
                    model_name=self._get_model_name(config)
                )
            
            # Set basic properties
            self._config = config
            self._model_name = self._get_model_name(config)
            
            # Get timeout from config if available
            self._timeout_seconds = config.get_value("timeout_seconds", self._timeout_seconds)
            
            # Create resource manager
            self._resource_manager = ModelResourceManager(self._model_name)
            
            # Call implementation-specific initialization
            logger.info(f"Initializing model: {self._model_name}")
            self._initialize_impl(config)
            
            # Mark as initialized
            self._is_initialized = True
            logger.info(f"Model initialized successfully: {self._model_name}")
            
        except ModelConfigError:
            # Re-raise configuration errors
            raise
        except ModelInitializationError as e:
            # Re-raise initialization errors
            self._cleanup_resources()
            raise
        except ModelResourceError as e:
            # Re-raise resource errors
            self._cleanup_resources()
            raise
        except Exception as e:
            # Wrap other exceptions in initialization error
            self._cleanup_resources()
            logger.exception(f"Failed to initialize model: {str(e)}")
            raise ModelInitializationError(
                f"Unexpected error during initialization: {str(e)}",
                model_name=self._model_name
            ) from e
    
    def process_image(self, image_path: Path) -> Dict[str, Any]:
        """
        Process an invoice image and extract information.
        
        This method:
        1. Validates initialization
        2. Validates the input image
        3. Preprocesses the image
        4. Performs inference with timeout
        5. Post-processes results
        
        Args:
            image_path: Path to the invoice image file
            
        Returns:
            Dict containing extracted information with standardized keys
            
        Raises:
            ModelProcessingError: If processing fails
            ModelInputError: If the input image is invalid
            ModelResourceError: If required resources are unavailable
            ModelTimeoutError: If processing exceeds time limits
            FileNotFoundError: If image file doesn't exist
        """
        try:
            # Check initialization
            self._validate_initialization()
            
            # Validate image path
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Load and validate image
            image = self._load_and_validate_image(image_path)
            
            # Process image with timeout
            start_time = time.time()
            try:
                results = self._process_image_with_timeout(image, image_path)
            except TimeoutError:
                elapsed = time.time() - start_time
                raise ModelTimeoutError(
                    "Image processing timed out",
                    model_name=self._model_name,
                    image_path=str(image_path),
                    timeout_seconds=self._timeout_seconds
                )
                
            # Return processed results
            return results
            
        except (
            ModelProcessingError,
            ModelInputError,
            ModelResourceError,
            ModelTimeoutError,
            FileNotFoundError
        ):
            # Re-raise known errors
            raise
        except Exception as e:
            # Wrap other exceptions in processing error
            logger.exception(f"Failed to process image: {str(e)}")
            raise ModelProcessingError(
                f"Unexpected error during processing: {str(e)}",
                model_name=self._model_name,
                image_path=str(image_path)
            ) from e
    
    def validate_config(self, config: BaseConfig) -> bool:
        """
        Validate model configuration.
        
        Base validation checks for required fields, then calls
        implementation-specific validation.
        
        Args:
            config: Model configuration
            
        Returns:
            True if configuration is valid
            
        Raises:
            ModelConfigError: If configuration is invalid
        """
        # Check basic required fields
        required_fields = ["name", "type", "version"]
        for field in required_fields:
            if not config.has_value(field):
                raise ModelConfigError(
                    f"Missing required configuration field",
                    model_name=self._get_model_name(config),
                    parameter=field
                )
        
        # Call implementation-specific validation
        return self._validate_config_impl(config)
    
    @abstractmethod
    def _initialize_impl(self, config: BaseConfig) -> None:
        """
        Implementation-specific initialization.
        
        This method should:
        1. Load model weights and resources
        2. Configure model parameters
        3. Set up any required processing pipelines
        
        Args:
            config: Validated model configuration
            
        Raises:
            ModelInitializationError: If initialization fails
            ModelResourceError: If required resources cannot be loaded
        """
        pass
    
    @abstractmethod
    def _process_image_impl(self, image: Image.Image, image_path: Path) -> Dict[str, Any]:
        """
        Implementation-specific image processing.
        
        This method should:
        1. Process the validated image
        2. Extract structured information
        3. Return data in standardized format
        
        Args:
            image: Validated PIL Image
            image_path: Original path to the image
            
        Returns:
            Dict containing extracted information
            
        Raises:
            ModelProcessingError: If processing fails
        """
        pass
    
    @abstractmethod
    def _validate_config_impl(self, config: BaseConfig) -> bool:
        """
        Implementation-specific configuration validation.
        
        This method should:
        1. Validate implementation-specific configuration
        2. Check for required parameters
        3. Verify parameter values
        
        Args:
            config: Model configuration to validate
            
        Returns:
            True if configuration is valid
            
        Raises:
            ModelConfigError: If configuration is invalid
        """
        pass
    
    def _validate_initialization(self) -> None:
        """
        Validate that the model has been initialized.
        
        Raises:
            ModelInitializationError: If model is not initialized
        """
        if not self._is_initialized:
            raise ModelInitializationError(
                "Model has not been initialized",
                model_name=self._model_name
            )
    
    def _get_model_name(self, config: Optional[BaseConfig] = None) -> str:
        """
        Get the model name from configuration or fallback.
        
        Args:
            config: Optional configuration
            
        Returns:
            Model name string
        """
        if self._model_name:
            return self._model_name
        
        if config and config.has_value("name"):
            return config.get_value("name")
        
        return self.__class__.__name__
    
    def _cleanup_resources(self) -> None:
        """
        Clean up all resources.
        Safe to call multiple times.
        """
        if self._resource_manager:
            logger.debug(f"Cleaning up resources for model: {self._model_name}")
            self._resource_manager.close_all()
    
    def _load_and_validate_image(self, image_path: Path) -> Image.Image:
        """
        Load and validate an image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Validated PIL Image
            
        Raises:
            ModelInputError: If image is invalid
            ModelResourceError: If image cannot be loaded
        """
        try:
            with self._resource_manager.open_file(image_path, 'rb') as f:
                image = Image.open(f)
                image.load()  # Ensure image is loaded fully
                
                # Validate image
                if image.mode not in ['RGB', 'RGBA', 'L']:
                    raise ModelInputError(
                        f"Unsupported image mode",
                        model_name=self._model_name,
                        input_name=str(image_path),
                        input_value=image.mode,
                        expected="RGB, RGBA, or L"
                    )
                
                # Return validated image
                return image
                
        except (IOError, OSError) as e:
            raise ModelResourceError(
                f"Failed to load image: {str(e)}",
                model_name=self._model_name,
                resource_type="image_file",
                resource_name=str(image_path)
            ) from e
    
    def _process_image_with_timeout(self, image: Image.Image, image_path: Path) -> Dict[str, Any]:
        """
        Process image with timeout handling.
        
        Args:
            image: Validated PIL Image
            image_path: Original path to the image
            
        Returns:
            Processed results
            
        Raises:
            TimeoutError: If processing exceeds timeout
            ModelProcessingError: If processing fails
        """
        # TODO: Implement proper timeout mechanism
        # Current implementation doesn't truly enforce timeout
        # This would be better with concurrent.futures or similar
        
        # For now, just call implementation
        return self._process_image_impl(image, image_path)
    
    def __del__(self) -> None:
        """Clean up resources when object is garbage collected."""
        self._cleanup_resources() 