"""Implementation of the DataLoader component.

This module provides the concrete implementation of the DataLoader interface
for loading and managing invoice images and ground truth data.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
from PIL import Image
import logging

from .base_data_loader import BaseDataLoader
from .ground_truth_manager import GroundTruthManager
from .exceptions import DataLoadError, GroundTruthError, ImageLoadError, DataValidationError


class DataLoader(BaseDataLoader):
    """Loads and manages invoice data and ground truth information.
    
    This class implements the BaseDataLoader interface, providing concrete
    implementations for loading and managing invoice images and their
    corresponding ground truth data.
    
    Attributes:
        data_dir: Path to the root data directory
        image_dir: Path to the directory containing invoice images
        ground_truth_file: Path to the ground truth CSV file
        _ground_truth_manager: Manager for handling ground truth data
        _loaded_images: Cache of loaded images
    """
    
    def __init__(
        self,
        data_dir: Path,
        ground_truth_manager: GroundTruthManager,
        image_dir: Optional[Path] = None,
        cache_enabled: bool = True
    ) -> None:
        """Initialize the DataLoader.
        
        Args:
            data_dir: Path to the root data directory
            ground_truth_manager: Manager for ground truth data handling
            image_dir: Optional path to image directory (default: data_dir/images)
            cache_enabled: Whether to cache loaded data (default: True)
            
        Raises:
            DataValidationError: If required directories or files don't exist
        """
        # Validate and set up paths
        if not data_dir.exists():
            raise DataValidationError(f"Data directory does not exist: {data_dir}")
            
        self.data_dir = data_dir
        self.image_dir = image_dir or data_dir / "images"
        
        # Validate image directory exists
        if not self.image_dir.exists():
            raise DataValidationError(f"Image directory does not exist: {self.image_dir}")
            
        # Set up dependencies through injection
        self._ground_truth_manager = ground_truth_manager
        
        # Set up image caching
        self.cache_enabled = cache_enabled
        self._loaded_images: Dict[str, Image.Image] = {}
        
        # Set up logging
        self._logger = logging.getLogger(__name__)
        
    def load_ground_truth(self) -> pd.DataFrame:
        """Load the ground truth data from CSV.
        
        Returns:
            DataFrame containing the ground truth data
            
        Raises:
            GroundTruthError: If there is an error loading the ground truth data
        """
        try:
            self._ground_truth_manager.validate_ground_truth()
            return self._ground_truth_manager._ground_truth_data
        except GroundTruthError as e:
            error_msg = f"Error loading ground truth data: {str(e)}"
            self._logger.error(error_msg)
            raise GroundTruthError(error_msg) from e
        
    def load_image(self, invoice_id: str) -> Image.Image:
        """Load an invoice image by its ID.
        
        Args:
            invoice_id: The invoice ID (filename without extension)
            
        Returns:
            PIL Image object for the invoice
            
        Raises:
            ImageLoadError: If there is an error loading the image
        """
        if invoice_id not in self._loaded_images or not self.cache_enabled:
            image_path = self.image_dir / f"{invoice_id}.jpg"
            if not image_path.exists():
                error_msg = f"Image not found: {image_path}"
                self._logger.error(error_msg)
                raise ImageLoadError(error_msg)
                
            try:
                image = Image.open(image_path)
                if self.cache_enabled:
                    self._loaded_images[invoice_id] = image
                self._logger.debug(f"Loaded image: {image_path}")
                return image
            except Exception as e:
                error_msg = f"Error loading image {image_path}: {str(e)}"
                self._logger.error(error_msg)
                raise ImageLoadError(error_msg) from e
                
        return self._loaded_images[invoice_id]
        
    def get_available_invoice_ids(self) -> List[str]:
        """Get a list of all available invoice IDs.
        
        Returns:
            List of invoice IDs that have both image and ground truth data
        """
        # Get all image files
        image_files = list(self.image_dir.glob("*.jpg"))
        image_ids = {f.stem for f in image_files}
        
        # Get all ground truth IDs from manager
        try:
            ground_truth = self.load_ground_truth()
            ground_truth_ids = set(ground_truth["Invoice"].astype(str))
        except GroundTruthError:
            ground_truth_ids = set()
        
        # Return IDs that have both image and ground truth
        valid_ids = sorted(image_ids.intersection(ground_truth_ids))
        self._logger.info(f"Found {len(valid_ids)} valid invoice IDs")
        return valid_ids
        
    def get_invoice_data(self, invoice_id: str) -> Tuple[Image.Image, Dict[str, str]]:
        """Get both the image and ground truth data for an invoice.
        
        Args:
            invoice_id: The invoice ID to retrieve
            
        Returns:
            Tuple of (image, ground_truth_data)
            where ground_truth_data is a dictionary with properly formatted values
            
        Raises:
            DataLoadError: If either the image or ground truth data cannot be loaded
        """
        try:
            # Load ground truth using manager for proper type handling
            ground_truth = self._ground_truth_manager.get_ground_truth(invoice_id)
        except GroundTruthError as e:
            error_msg = f"Invoice ID {invoice_id} not found in ground truth data"
            self._logger.error(error_msg)
            raise DataLoadError(error_msg) from e
            
        try:
            # Load image
            image = self.load_image(invoice_id)
        except ImageLoadError as e:
            error_msg = f"Failed to load image for invoice {invoice_id}"
            self._logger.error(error_msg)
            raise DataLoadError(error_msg) from e
            
        return image, ground_truth
        
    def clear_cache(self) -> None:
        """Clear the image and ground truth caches."""
        self._loaded_images.clear()
        self._ground_truth_manager.clear_cache()
        self._logger.debug("Cleared data caches")
