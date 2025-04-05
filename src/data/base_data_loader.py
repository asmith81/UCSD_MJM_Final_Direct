"""Base interface for data loading components.

This module defines the interface that all data loader implementations must follow.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Tuple
from PIL import Image
import pandas as pd


class BaseDataLoader(ABC):
    """Base interface for data loading components.
    
    This abstract base class defines the contract that all data loader
    implementations must fulfill. It provides methods for loading and
    managing invoice images and their corresponding ground truth data.
    """
    
    @abstractmethod
    def load_ground_truth(self) -> pd.DataFrame:
        """Load the ground truth data from CSV.
        
        Returns:
            DataFrame containing the ground truth data
            
        Raises:
            FileNotFoundError: If the ground truth file doesn't exist
            pd.errors.EmptyDataError: If the CSV file is empty
            pd.errors.ParserError: If the CSV file is malformed
        """
        pass
        
    @abstractmethod
    def load_image(self, invoice_id: str) -> Image.Image:
        """Load an invoice image by its ID.
        
        Args:
            invoice_id: The invoice ID (filename without extension)
            
        Returns:
            PIL Image object for the invoice
            
        Raises:
            FileNotFoundError: If the image file doesn't exist
            PIL.UnidentifiedImageError: If the image file is corrupt or invalid
        """
        pass
        
    @abstractmethod
    def get_available_invoice_ids(self) -> List[str]:
        """Get a list of all available invoice IDs.
        
        Returns:
            List of invoice IDs that have both image and ground truth data
        """
        pass
        
    @abstractmethod
    def get_invoice_data(self, invoice_id: str) -> Tuple[Image.Image, pd.Series]:
        """Get both the image and ground truth data for an invoice.
        
        Args:
            invoice_id: The invoice ID to retrieve
            
        Returns:
            Tuple of (image, ground_truth_row)
            
        Raises:
            KeyError: If the invoice ID is not found in ground truth
            FileNotFoundError: If the image file is not found
        """
        pass
        
    @abstractmethod
    def clear_cache(self) -> None:
        """Clear any cached data."""
        pass 