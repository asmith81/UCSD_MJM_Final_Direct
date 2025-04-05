"""Factory for creating DataLoader instances."""

from pathlib import Path
from typing import Optional, Type, Dict

from .base_data_loader import BaseDataLoader
from .data_loader import DataLoader


class DataLoaderFactory:
    """Factory for creating data loader instances.
    
    This factory follows the project's factory pattern requirements and provides
    a centralized way to create data loader instances with proper configuration.
    """
    
    # Registry of available implementations
    REGISTRY: Dict[str, Type[BaseDataLoader]] = {
        "default": DataLoader
    }
    
    @classmethod
    def register_implementation(cls, name: str, implementation: Type[BaseDataLoader]) -> None:
        """Register a new data loader implementation.
        
        Args:
            name: Name to register the implementation under
            implementation: The data loader class to register
        """
        cls.REGISTRY[name] = implementation
        
    @classmethod
    def create_data_loader(
        cls,
        data_dir: Path,
        loader_type: str = "default",
        image_dir: Optional[Path] = None,
        ground_truth_file: Optional[Path] = None,
        cache_enabled: bool = True
    ) -> BaseDataLoader:
        """Create a data loader instance.
        
        Args:
            data_dir: Path to the root data directory
            loader_type: Type of loader to create (default: "default")
            image_dir: Optional path to image directory
            ground_truth_file: Optional path to ground truth CSV
            cache_enabled: Whether to enable caching (default: True)
            
        Returns:
            BaseDataLoader: The created data loader instance
            
        Raises:
            ValueError: If loader_type is not supported
        """
        if loader_type not in cls.REGISTRY:
            raise ValueError(
                f"Unsupported loader type: {loader_type}. "
                f"Available types: {list(cls.REGISTRY.keys())}"
            )
            
        loader_class = cls.REGISTRY[loader_type]
        return loader_class(
            data_dir=data_dir,
            image_dir=image_dir,
            ground_truth_file=ground_truth_file,
            cache_enabled=cache_enabled
        ) 