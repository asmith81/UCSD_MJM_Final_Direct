"""
Model Error Hierarchy.

This module defines a comprehensive hierarchy of exceptions for model-related errors.
Each exception type provides detailed context and appropriate error messaging.
"""
from typing import Any, Optional


class ModelError(Exception):
    """Base exception for all model-related errors."""
    
    def __init__(self, message: str, model_name: Optional[str] = None):
        """
        Initialize with error message and optional context.
        
        Args:
            message: Error message describing the issue
            model_name: Optional name of the model where error occurred
        """
        self.model_name = model_name
        prefix = f"[{model_name}] " if model_name else ""
        super().__init__(f"{prefix}{message}")


class ModelInitializationError(ModelError):
    """
    Raised when a model fails to initialize properly.
    
    This exception indicates issues with:
    - Model weight loading
    - Resource allocation
    - Dependency initialization
    - Configuration validation
    """
    
    def __init__(
        self, 
        message: str, 
        model_name: Optional[str] = None,
        component: Optional[str] = None
    ):
        """
        Initialize with error details.
        
        Args:
            message: Error message describing the initialization failure
            model_name: Optional name of the model
            component: Optional component that failed to initialize
        """
        self.component = component
        component_info = f" in component '{component}'" if component else ""
        super().__init__(f"Initialization failed{component_info}: {message}", model_name)


class ModelConfigError(ModelError):
    """
    Raised when model configuration is invalid.
    
    This exception indicates issues with:
    - Missing required configuration
    - Invalid parameter values
    - Incompatible configuration settings
    """
    
    def __init__(
        self, 
        message: str, 
        model_name: Optional[str] = None,
        parameter: Optional[str] = None,
        value: Any = None,
        expected: Any = None
    ):
        """
        Initialize with configuration error details.
        
        Args:
            message: Error message describing the configuration issue
            model_name: Optional name of the model
            parameter: Optional name of the invalid parameter
            value: Optional invalid value provided
            expected: Optional description of expected value
        """
        self.parameter = parameter
        self.value = value
        self.expected = expected
        
        if parameter:
            if value is not None and expected is not None:
                message = f"Invalid configuration parameter '{parameter}': {message}. Got '{value}', expected {expected}"
            elif value is not None:
                message = f"Invalid configuration parameter '{parameter}': {message}. Got '{value}'"
            else:
                message = f"Invalid configuration parameter '{parameter}': {message}"
                
        super().__init__(message, model_name)


class ModelResourceError(ModelError):
    """
    Raised when model resource management fails.
    
    This exception indicates issues with:
    - Memory allocation
    - File access
    - External service connectivity
    - Missing dependencies
    """
    
    def __init__(
        self, 
        message: str, 
        model_name: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_name: Optional[str] = None
    ):
        """
        Initialize with resource error details.
        
        Args:
            message: Error message describing the resource issue
            model_name: Optional name of the model
            resource_type: Optional type of resource (memory, file, etc.)
            resource_name: Optional name/identifier of the resource
        """
        self.resource_type = resource_type
        self.resource_name = resource_name
        
        resource_info = ""
        if resource_type and resource_name:
            resource_info = f" for {resource_type} '{resource_name}'"
        elif resource_type:
            resource_info = f" for {resource_type}"
        elif resource_name:
            resource_info = f" for '{resource_name}'"
            
        super().__init__(f"Resource error{resource_info}: {message}", model_name)


class ModelProcessingError(ModelError):
    """
    Raised when a model fails to process an image.
    
    This exception indicates issues with:
    - Input validation
    - Processing pipeline errors
    - Inference failures
    - Output formatting
    """
    
    def __init__(
        self, 
        message: str, 
        model_name: Optional[str] = None,
        image_path: Optional[str] = None,
        processing_stage: Optional[str] = None
    ):
        """
        Initialize with processing error details.
        
        Args:
            message: Error message describing the processing issue
            model_name: Optional name of the model
            image_path: Optional path of the image being processed
            processing_stage: Optional stage where processing failed
        """
        self.image_path = image_path
        self.processing_stage = processing_stage
        
        context = []
        if image_path:
            context.append(f"image '{image_path}'")
        if processing_stage:
            context.append(f"during {processing_stage}")
            
        context_str = " " + ", ".join(context) if context else ""
        super().__init__(f"Processing failed{context_str}: {message}", model_name)


class ModelInputError(ModelError):
    """
    Raised when model input validation fails.
    
    This exception indicates issues with:
    - Invalid input format
    - Missing required inputs
    - Corrupt input data
    """
    
    def __init__(
        self, 
        message: str, 
        model_name: Optional[str] = None,
        input_name: Optional[str] = None,
        input_value: Any = None,
        expected: Any = None
    ):
        """
        Initialize with input error details.
        
        Args:
            message: Error message describing the input issue
            model_name: Optional name of the model
            input_name: Optional name of the invalid input
            input_value: Optional invalid value provided
            expected: Optional description of expected value
        """
        self.input_name = input_name
        self.input_value = input_value
        self.expected = expected
        
        if input_name:
            if input_value is not None and expected is not None:
                message = f"Invalid input '{input_name}': {message}. Got '{input_value}', expected {expected}"
            elif input_value is not None:
                message = f"Invalid input '{input_name}': {message}. Got '{input_value}'"
            else:
                message = f"Invalid input '{input_name}': {message}"
                
        super().__init__(message, model_name)


class ModelTimeoutError(ModelProcessingError):
    """
    Raised when model processing exceeds time limits.
    
    This exception indicates issues with:
    - Processing taking too long
    - Resource contention
    - Algorithmic inefficiencies
    """
    
    def __init__(
        self, 
        message: str, 
        model_name: Optional[str] = None,
        image_path: Optional[str] = None,
        timeout_seconds: Optional[float] = None
    ):
        """
        Initialize with timeout error details.
        
        Args:
            message: Error message describing the timeout issue
            model_name: Optional name of the model
            image_path: Optional path of the image being processed
            timeout_seconds: Optional timeout threshold in seconds
        """
        self.timeout_seconds = timeout_seconds
        
        timeout_info = f" after {timeout_seconds}s" if timeout_seconds is not None else ""
        super().__init__(f"Timeout{timeout_info}: {message}", model_name, image_path, "inference")


class ModelCreationError(ModelError):
    """
    Raised when model creation fails.
    
    This exception indicates issues with:
    - Factory configuration
    - Model registration
    - Dependency resolution
    """
    
    def __init__(
        self, 
        message: str, 
        model_name: Optional[str] = None,
        model_type: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        """
        Initialize with creation error details.
        
        Args:
            message: Error message describing the creation issue
            model_name: Optional name of the model being created
            model_type: Optional type of the model being created
            cause: Optional underlying exception that caused this error
        """
        self.model_type = model_type
        self.cause = cause
        
        if model_type and model_type != model_name:
            type_info = f" (type: {model_type})"
        else:
            type_info = ""
            
        super().__init__(f"Creation failed{type_info}: {message}", model_name) 