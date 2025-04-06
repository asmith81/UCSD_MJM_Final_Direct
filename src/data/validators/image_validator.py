"""Image validator implementation.

This module provides a validator for image data, ensuring that
images meet the required quality and format standards.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import numpy as np
from PIL import Image, UnidentifiedImageError


from .base_validator import BaseValidator


class ImageValidator(BaseValidator):
    """Validator for image data.
    
    This validator ensures that images meet format and quality requirements.
    
    Attributes:
        min_width: Minimum acceptable image width
        min_height: Minimum acceptable image height
        max_size_mb: Maximum acceptable file size in MB
        allowed_formats: Set of allowed image format extensions
    """
    
    def __init__(
        self,
        min_width: int = 500,
        min_height: int = 500,
        max_size_mb: float = 10.0,
        allowed_formats: Optional[Set[str]] = None,
        strict_mode: bool = True
    ) -> None:
        """Initialize the image validator.
        
        Args:
            min_width: Minimum acceptable width in pixels (default: 500)
            min_height: Minimum acceptable height in pixels (default: 500)
            max_size_mb: Maximum file size in MB (default: 10.0)
            allowed_formats: Set of allowed extensions (default: {'.jpg', '.jpeg', '.png'})
            strict_mode: Whether to use strict validation (default: True)
        """
        super().__init__(strict_mode=strict_mode)
        self.min_width = min_width
        self.min_height = min_height
        self.max_size_mb = max_size_mb
        self.allowed_formats = allowed_formats or {'.jpg', '.jpeg', '.png'}
        self._logger = logging.getLogger(__name__)
        
    def validate(self, image_path: Union[str, Path]) -> bool:
        """Validate an image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            True if validation passes, False otherwise
        """
        self.clear_errors()
        path = Path(image_path)
        
        # Check file exists
        if not path.exists():
            self.add_error(f"Image file does not exist: {path}")
            return False
            
        # Check file extension
        if path.suffix.lower() not in self.allowed_formats:
            self.add_error(
                f"Invalid image format: {path.suffix}. "
                f"Allowed formats: {', '.join(self.allowed_formats)}"
            )
            
        # Check file size
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.max_size_mb:
            self.add_error(
                f"Image file too large: {file_size_mb:.2f} MB. "
                f"Maximum allowed: {self.max_size_mb} MB"
            )
            
        # Try to open and validate image properties
        try:
            with Image.open(path) as img:
                width, height = img.size
                
                # Check dimensions
                if width < self.min_width:
                    self.add_error(
                        f"Image width too small: {width}px. "
                        f"Minimum required: {self.min_width}px"
                    )
                    
                if height < self.min_height:
                    self.add_error(
                        f"Image height too small: {height}px. "
                        f"Minimum required: {self.min_height}px"
                    )
                    
                # Check if image can be converted to array
                try:
                    _ = np.array(img)
                except Exception as e:
                    self.add_error(f"Cannot convert image to array: {str(e)}")
                    
        except UnidentifiedImageError:
            self.add_error(f"Cannot identify image format: {path}")
        except Exception as e:
            self.add_error(f"Error validating image: {str(e)}")
            
        valid = not self.has_errors()
        self._logger.info(f"Image validation {'passed' if valid else 'failed'} for {path}")
        
        return valid
        
    def get_image_info(self, image_path: Union[str, Path]) -> Dict[str, Any]:
        """Get information about an image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with image properties
        """
        path = Path(image_path)
        info = {
            "path": str(path),
            "exists": path.exists(),
            "size_mb": path.stat().st_size / (1024 * 1024) if path.exists() else 0,
            "format": path.suffix,
            "valid": False,
            "width": 0,
            "height": 0,
            "mode": None
        }
        
        if not path.exists():
            return info
            
        try:
            with Image.open(path) as img:
                info.update({
                    "width": img.size[0],
                    "height": img.size[1],
                    "aspect_ratio": img.size[0] / img.size[1],
                    "mode": img.mode,
                    "format": img.format,
                    "valid": True
                })
        except Exception as e:
            self._logger.error(f"Error getting image info: {str(e)}")
            
        return info
        
    def validate_batch(self, image_paths: List[Union[str, Path]]) -> Dict[str, Any]:
        """Validate a batch of images.
        
        Args:
            image_paths: List of paths to image files
            
        Returns:
            Dictionary with batch validation results
        """
        results = {
            "total": len(image_paths),
            "valid": 0,
            "invalid": 0,
            "invalid_paths": [],
            "details": {},
        }
        
        for path in image_paths:
            path_str = str(path)
            valid = self.validate(path)
            
            results["details"][path_str] = {
                "valid": valid,
                "errors": self.get_errors().copy() if not valid else []
            }
            
            if valid:
                results["valid"] += 1
            else:
                results["invalid"] += 1
                results["invalid_paths"].append(path_str)
                
            # Clear errors for next image
            self.clear_errors()
            
        return results 