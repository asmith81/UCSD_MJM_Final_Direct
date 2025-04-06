"""Factory for creating image processor instances."""

from typing import Dict, Type
from src.config.base_config import BaseConfig
from src.image.base_image_processor import BaseImageProcessor
from src.image.image_processor import ImageProcessor
from src.image.exceptions import ConfigurationError

class ImageProcessorFactory:
    """Factory for creating image processor instances."""
    
    # Registry of available processor implementations
    REGISTRY: Dict[str, Type[BaseImageProcessor]] = {
        "default": ImageProcessor
    }
    
    @classmethod
    def register_processor(
        cls,
        name: str,
        processor_class: Type[BaseImageProcessor]
    ) -> None:
        """Register a new processor implementation.
        
        Args:
            name: Name to register the processor under
            processor_class: The processor class to register
            
        Raises:
            ValueError: If name is already registered
        """
        if name in cls.REGISTRY:
            raise ValueError(f"Processor type already registered: {name}")
        cls.REGISTRY[name] = processor_class
        
    def create_processor(
        self,
        processor_type: str = "default",
        config: BaseConfig = None
    ) -> BaseImageProcessor:
        """Create an image processor instance.
        
        Args:
            processor_type: Type of processor to create (default: "default")
            config: Processor configuration
            
        Returns:
            BaseImageProcessor: The created processor instance
            
        Raises:
            ValueError: If processor_type is not supported
            ConfigurationError: If configuration is invalid
        """
        if processor_type not in self.REGISTRY:
            raise ValueError(
                f"Unsupported processor type: {processor_type}. "
                f"Available types: {list(self.REGISTRY.keys())}"
            )
            
        # Create processor instance
        processor_class = self.REGISTRY[processor_type]
        processor = processor_class()
        
        # Initialize if config provided
        if config is not None:
            try:
                processor.initialize(config)
            except Exception as e:
                raise ConfigurationError(f"Failed to initialize processor: {str(e)}")
                
        return processor 