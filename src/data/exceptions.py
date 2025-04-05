"""Custom exceptions for data loading components."""


class DataLoadError(Exception):
    """Base exception for data loading errors."""
    pass


class GroundTruthError(DataLoadError):
    """Raised when there is an error with ground truth data."""
    pass


class ImageLoadError(DataLoadError):
    """Raised when there is an error loading an image."""
    pass


class DataValidationError(DataLoadError):
    """Raised when data validation fails."""
    pass 