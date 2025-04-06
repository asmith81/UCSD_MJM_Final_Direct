"""Exceptions for image processing operations."""

class ImageProcessingError(Exception):
    """Base exception for image processing errors."""
    pass

class ImageValidationError(ImageProcessingError):
    """Raised when an image fails validation."""
    pass

class ConfigurationError(ImageProcessingError):
    """Raised when image processor configuration is invalid."""
    pass 