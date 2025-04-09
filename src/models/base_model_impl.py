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
from .error_recovery import ErrorRecoveryManager, with_error_recovery
from .model_errors import (
    ModelInitializationError,
    ModelConfigError, 
    ModelProcessingError,
    ModelResourceError,
    ModelInputError,
    ModelTimeoutError,
    ModelLoaderTimeoutError
)
from .model_loading_timeout import load_model_with_timeout
from .model_resource_manager import ModelResourceManager
from .retry_utils import RetryConfig, with_retry

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
        self._timeout_seconds = 60.0  # Default processing timeout
        self._loading_timeout_seconds = 300.0  # Default loading timeout (5 min)
        self._retry_config = RetryConfig(
            max_attempts=3,
            delay_seconds=1.0,
            backoff_factor=2.0,
            max_delay_seconds=30.0
        )
        self._recovery_manager = None
        
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
            ModelLoaderTimeoutError: If loading exceeds time limit
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
            
            # Get timeouts from config if available
            self._timeout_seconds = config.get_value("timeout_seconds", self._timeout_seconds)
            self._loading_timeout_seconds = config.get_value("loading_timeout_seconds", self._loading_timeout_seconds)
            
            # Create resource manager
            self._resource_manager = ModelResourceManager(self._model_name)
            
            # Create recovery manager
            self._recovery_manager = ErrorRecoveryManager(self._resource_manager, self._model_name)
            
            # Call implementation-specific initialization with timeout
            logger.info(f"Initializing model: {self._model_name}")
            
            # Load the model with timeout handling
            self._load_model_with_timeout(config)
            
            # Mark as initialized
            self._is_initialized = True
            logger.info(f"Model initialized successfully: {self._model_name}")
            
        except ModelConfigError:
            # Re-raise configuration errors
            raise
        except ModelInitializationError as e:
            # Re-raise initialization errors after cleanup
            self._cleanup_resources()
            raise
        except ModelResourceError as e:
            # Re-raise resource errors after cleanup
            self._cleanup_resources()
            raise
        except ModelLoaderTimeoutError as e:
            # Re-raise timeout errors after cleanup
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
    
    def _load_model_with_timeout(self, config: BaseConfig) -> None:
        """
        Load the model with timeout handling.
        
        Args:
            config: Validated model configuration
            
        Raises:
            ModelLoaderTimeoutError: If loading exceeds time limit
            ModelInitializationError: If initialization fails
            ModelResourceError: If required resources cannot be loaded
        """
        try:
            # Create loader function that will be executed with timeout
            def loader_func():
                return self._initialize_impl(config)
                
            # Load model with timeout
            load_model_with_timeout(
                loader_func,
                self._loading_timeout_seconds,
                model_name=self._model_name,
                component="model_initialization"
            )
            
        except TimeoutError as e:
            # Convert generic TimeoutError to ModelLoaderTimeoutError
            raise ModelLoaderTimeoutError(
                "Model initialization timed out",
                model_name=self._model_name,
                timeout_seconds=self._loading_timeout_seconds
            ) from e
    
    @with_error_recovery(operation_name="process_image")
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
                    f"Image processing timed out after {elapsed:.1f}s",
                    model_name=self._model_name,
                    image_path=str(image_path),
                    timeout_seconds=elapsed
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
        try:
            # Check for basic required fields
            if not config:
                raise ModelConfigError(
                    "Configuration is empty",
                    model_name=self._get_model_name(config)
                )
                
            # Call implementation-specific validation
            return self._validate_config_impl(config)
            
        except ModelConfigError:
            # Re-raise ModelConfigError
            raise
        except Exception as e:
            # Wrap other exceptions in ModelConfigError
            model_name = self._get_model_name(config)
            raise ModelConfigError(
                f"Unexpected error during configuration validation: {str(e)}",
                model_name=model_name
            ) from e
    
    def _validate_initialization(self) -> None:
        """
        Validate that the model is initialized.
        
        Raises:
            ModelInitializationError: If model is not initialized
        """
        if not self._is_initialized:
            raise ModelInitializationError(
                "Model is not initialized. Call initialize() first.",
                model_name=self._model_name
            )
    
    @with_retry()
    def _process_image_with_timeout(self, image: Image.Image, image_path: Path) -> Dict[str, Any]:
        """
        Process image with timeout handling and retry support.
        
        Args:
            image: Validated PIL Image
            image_path: Path to the image file
            
        Returns:
            Dict containing extracted information
            
        Raises:
            ModelProcessingError: If processing fails
            ModelTimeoutError: If processing exceeds time limit
        """
        # Execute with timeout
        with self._recovery_manager.recovery_context("image_processing"):
            try:
                start_time = time.time()
                
                # Process with timeout
                def processing_func():
                    return self._process_image_impl(image, image_path)
                    
                # Use ThreadPoolExecutor for timeout
                return load_model_with_timeout(
                    processing_func, 
                    self._timeout_seconds,
                    model_name=self._model_name,
                    component="image_processing",
                    resource_name=str(image_path)
                )
                
            except TimeoutError:
                elapsed = time.time() - start_time
                raise ModelTimeoutError(
                    "Image processing operation timed out",
                    model_name=self._model_name,
                    image_path=str(image_path),
                    timeout_seconds=elapsed
                )
                
    def _load_and_validate_image(self, image_path: Path) -> Image.Image:
        """
        Load and validate an image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            PIL Image object
            
        Raises:
            ModelInputError: If image is invalid or corrupt
        """
        try:
            # Load image with PIL
            image = Image.open(image_path)
            
            # Validate image
            if not image:
                raise ModelInputError(
                    "Failed to load image",
                    model_name=self._model_name,
                    input_name="image_path",
                    input_value=str(image_path)
                )
                
            # Ensure image is loaded
            image.load()
            
            return image
            
        except (IOError, OSError) as e:
            # Handle PIL errors
            raise ModelInputError(
                f"Invalid or corrupt image file: {str(e)}",
                model_name=self._model_name,
                input_name="image_path",
                input_value=str(image_path)
            ) from e
    
    def _cleanup_resources(self) -> None:
        """Clean up resources after initialization failure."""
        if self._resource_manager:
            try:
                self._resource_manager.close_all()
                logger.debug("Cleaned up resources after initialization failure")
            except Exception as e:
                logger.warning(f"Error cleaning up resources: {str(e)}")
    
    def _get_model_name(self, config: Optional[BaseConfig] = None) -> Optional[str]:
        """Get model name from config or instance variable."""
        if self._model_name:
            return self._model_name
            
        if config and config.has_value("name"):
            return config.get_value("name")
            
        return self.__class__.__name__
    
    @abstractmethod
    def _initialize_impl(self, config: BaseConfig) -> None:
        """
        Implementation-specific initialization.
        
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
        
        Args:
            image: Validated PIL Image
            image_path: Path to the image file
            
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
        
        Args:
            config: Model configuration
            
        Returns:
            True if configuration is valid
            
        Raises:
            ModelConfigError: If configuration is invalid
        """
        pass 