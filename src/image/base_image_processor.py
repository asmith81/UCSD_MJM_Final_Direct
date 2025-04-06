"""Base interface for image processors."""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from PIL import Image
from src.config.base_config import BaseConfig

class BaseImageProcessor(ABC):
    """Abstract base class for image processors.
    
    This class defines the interface for image preprocessing components
    that handle operations like resizing, color conversion, and normalization.
    """
    
    @abstractmethod
    def initialize(self, config: BaseConfig) -> None:
        """Initialize with configuration.
        
        Args:
            config: Image processor configuration
        """
        pass
        
    @abstractmethod
    def validate_image(self, image: Image.Image) -> bool:
        """Validate that an image meets processing requirements.
        
        Args:
            image: Input PIL Image
            
        Returns:
            bool: True if image is valid, False otherwise
        """
        pass
        
    @abstractmethod
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess a single image according to configuration.
        
        Args:
            image: Input PIL Image
            
        Returns:
            Image.Image: Preprocessed image
        """
        pass
        
    @abstractmethod
    def batch_preprocess(self, images: List[Image.Image]) -> List[Image.Image]:
        """Preprocess multiple images.
        
        Args:
            images: List of input PIL Images
            
        Returns:
            List[Image.Image]: List of preprocessed images
        """
        pass 