"""Implementation of the image processor component."""

from typing import List, Tuple, Optional
import numpy as np
from PIL import Image, ImageEnhance
from src.config.base_config import BaseConfig
from src.image.base_image_processor import BaseImageProcessor
from src.image.exceptions import ImageProcessingError, ImageValidationError, ConfigurationError

class ImageProcessor(BaseImageProcessor):
    """Concrete implementation of image preprocessing operations."""
    
    def __init__(self) -> None:
        """Initialize the image processor."""
        self.config = None
        self._initialized = False
        
    def initialize(self, config: BaseConfig) -> None:
        """Initialize with configuration.
        
        Args:
            config: Image processor configuration
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        try:
            self.config = config
            self._validate_config()
            self._initialized = True
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize image processor: {str(e)}")
            
    def _validate_config(self) -> None:
        """Validate the configuration."""
        if not self.config:
            raise ConfigurationError("Configuration not provided")
            
        config_data = self.config.get_data()
        required_fields = ['target_size', 'color_mode', 'normalize', 'maintain_aspect_ratio']
        
        for field in required_fields:
            if field not in config_data:
                raise ConfigurationError(f"Missing required field: {field}")
                
    def validate_image(self, image: Image.Image) -> bool:
        """Validate that an image meets processing requirements.
        
        Args:
            image: Input PIL Image
            
        Returns:
            bool: True if image is valid, False otherwise
        """
        if not isinstance(image, Image.Image):
            return False
            
        try:
            # Verify image can be converted to array
            _ = np.array(image)
            return True
        except Exception:
            return False
            
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess a single image according to configuration.
        
        Args:
            image: Input PIL Image
            
        Returns:
            Image.Image: Preprocessed image
            
        Raises:
            ImageProcessingError: If processing fails
            ImageValidationError: If image is invalid
        """
        if not self._initialized:
            raise ImageProcessingError("Image processor not initialized")
            
        if not self.validate_image(image):
            raise ImageValidationError("Invalid image provided")
            
        try:
            # Get configuration
            config_data = self.config.get_data()
            
            # Process image
            processed = image
            
            # Resize if needed
            if config_data['target_size']:
                processed = self._resize_image(
                    processed,
                    config_data['target_size'],
                    config_data['maintain_aspect_ratio']
                )
                
            # Convert color mode if needed
            if config_data['color_mode'] != processed.mode:
                processed = processed.convert(config_data['color_mode'])
                
            # Apply enhancements if specified
            processed = self._apply_enhancements(processed, config_data)
            
            # Normalize if requested
            if config_data['normalize']:
                processed = self._normalize_image(processed)
                
            return processed
            
        except Exception as e:
            raise ImageProcessingError(f"Failed to process image: {str(e)}")
            
    def batch_preprocess(self, images: List[Image.Image]) -> List[Image.Image]:
        """Preprocess multiple images.
        
        Args:
            images: List of input PIL Images
            
        Returns:
            List[Image.Image]: List of preprocessed images
            
        Raises:
            ImageProcessingError: If processing fails
        """
        if not self._initialized:
            raise ImageProcessingError("Image processor not initialized")
            
        processed_images = []
        errors = []
        
        for idx, image in enumerate(images):
            try:
                processed = self.preprocess_image(image)
                processed_images.append(processed)
            except Exception as e:
                errors.append(f"Error processing image {idx}: {str(e)}")
                
        if errors:
            raise ImageProcessingError(
                f"Batch processing failed for some images:\n" + "\n".join(errors)
            )
            
        return processed_images
        
    def _resize_image(
        self,
        image: Image.Image,
        target_size: Tuple[int, int],
        maintain_aspect_ratio: bool
    ) -> Image.Image:
        """Resize image to target size.
        
        Args:
            image: Input image
            target_size: Desired (width, height)
            maintain_aspect_ratio: Whether to maintain aspect ratio
            
        Returns:
            Image.Image: Resized image
        """
        if maintain_aspect_ratio:
            # Calculate new size maintaining aspect ratio
            ratio = min(
                target_size[0] / image.size[0],
                target_size[1] / image.size[1]
            )
            new_size = tuple(int(dim * ratio) for dim in image.size)
            return image.resize(new_size, Image.Resampling.LANCZOS)
        else:
            return image.resize(target_size, Image.Resampling.LANCZOS)
            
    def _normalize_image(self, image: Image.Image) -> Image.Image:
        """Normalize pixel values to [0,1] range.
        
        Args:
            image: Input image
            
        Returns:
            Image.Image: Normalized image
        """
        img_array = np.array(image).astype(np.float32)
        img_array = img_array / 255.0
        return Image.fromarray((img_array * 255).astype(np.uint8))
        
    def _apply_enhancements(self, image: Image.Image, config_data: dict) -> Image.Image:
        """Apply image enhancements based on configuration.
        
        Args:
            image: Input image
            config_data: Configuration dictionary
            
        Returns:
            Image.Image: Enhanced image
        """
        enhanced = image
        
        if config_data.get('contrast_factor'):
            enhancer = ImageEnhance.Contrast(enhanced)
            enhanced = enhancer.enhance(config_data['contrast_factor'])
            
        if config_data.get('brightness_factor'):
            enhancer = ImageEnhance.Brightness(enhanced)
            enhanced = enhancer.enhance(config_data['brightness_factor'])
            
        if config_data.get('sharpness_factor'):
            enhancer = ImageEnhance.Sharpness(enhanced)
            enhanced = enhancer.enhance(config_data['sharpness_factor'])
            
        return enhanced 