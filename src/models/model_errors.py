"""
Model Error Hierarchy.

This module defines a comprehensive hierarchy of exceptions for model-related errors.
Each exception type provides detailed context and appropriate error messaging.
"""
from typing import Any, Optional, Dict, List


class ModelError(Exception):
    """Base exception for all model-related errors."""
    
    def __init__(
        self, 
        message: str, 
        model_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with error message and optional context.
        
        Args:
            message: Error message describing the issue
            model_name: Optional name of the model where error occurred
            context: Optional dictionary with additional error context
        """
        self.model_name = model_name
        self.context = context or {}
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
        component: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with error details.
        
        Args:
            message: Error message describing the initialization failure
            model_name: Optional name of the model
            component: Optional component that failed to initialize
            context: Optional dictionary with additional error context
        """
        self.component = component
        context = context or {}
        if component:
            context["component"] = component
            
        component_info = f" in component '{component}'" if component else ""
        super().__init__(f"Initialization failed{component_info}: {message}", model_name, context)


class ModelConfigError(Exception):
    """Exception raised for model configuration errors."""

    def __init__(
        self,
        message: str,
        parameter: Optional[str] = None,
        value: Optional[Any] = None,
        expected: Optional[str] = None,
        model_name: Optional[str] = None,
        parent_error: Optional[Exception] = None,
        errors: Optional[List[str]] = None
    ):
        """Initialize ModelConfigError.

        Args:
            message: The error message
            parameter: The parameter that caused the error
            value: The invalid value
            expected: Description of expected value
            model_name: Name of the model being configured
            parent_error: Parent exception if this wraps another error
            errors: List of additional error messages
        """
        message_parts = []
        
        # Add base message
        message_parts.append(message.rstrip("."))
        
        # Add parameter and value context if provided
        if parameter is not None:
            if value is not None:
                message_parts.append(f"Got {value!r} for {parameter}")
            else:
                message_parts.append(f"Parameter: {parameter}")
        elif value is not None:
            message_parts.append(f"Got: {value!r}")
            
        # Add expected value if provided
        if expected is not None:
            message_parts.append(f"Expected: {expected}")
            
        # Add model name context if provided
        if model_name:
            message_parts.append(f"Model: {model_name}")
            
        # Add parent error if provided
        if parent_error:
            message_parts.append(f"Caused by: {str(parent_error)}")
            
        # Add additional errors if provided
        if errors:
            message_parts.extend(errors)
            
        # Join all parts with periods
        final_message = ". ".join(message_parts)
        
        # Ensure message ends with period
        if not final_message.endswith("."):
            final_message += "."
            
        super().__init__(final_message)


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
        resource_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with resource error details.
        
        Args:
            message: Error message describing the resource issue
            model_name: Optional name of the model
            resource_type: Optional type of resource (memory, file, etc.)
            resource_name: Optional name/identifier of the resource
            context: Optional dictionary with additional error context
        """
        self.resource_type = resource_type
        self.resource_name = resource_name
        
        context = context or {}
        if resource_type:
            context["resource_type"] = resource_type
        if resource_name:
            context["resource_name"] = resource_name
        
        resource_info = ""
        if resource_type and resource_name:
            resource_info = f" for {resource_type} '{resource_name}'"
        elif resource_type:
            resource_info = f" for {resource_type}"
        elif resource_name:
            resource_info = f" for '{resource_name}'"
            
        super().__init__(f"Resource error{resource_info}: {message}", model_name, context)


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
        processing_stage: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with processing error details.
        
        Args:
            message: Error message describing the processing issue
            model_name: Optional name of the model
            image_path: Optional path of the image being processed
            processing_stage: Optional stage where processing failed
            context: Optional dictionary with additional error context
        """
        self.image_path = image_path
        self.processing_stage = processing_stage
        
        context = context or {}
        if image_path:
            context["image_path"] = image_path
        if processing_stage:
            context["processing_stage"] = processing_stage
        
        context_parts = []
        if image_path:
            context_parts.append(f"image '{image_path}'")
        if processing_stage:
            context_parts.append(f"during {processing_stage}")
            
        context_str = " " + ", ".join(context_parts) if context_parts else ""
        super().__init__(f"Processing failed{context_str}: {message}", model_name, context)


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
        expected: Any = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with input error details.
        
        Args:
            message: Error message describing the input issue
            model_name: Optional name of the model
            input_name: Optional name of the invalid input
            input_value: Optional invalid value provided
            expected: Optional description of expected value
            context: Optional dictionary with additional error context
        """
        self.input_name = input_name
        self.input_value = input_value
        self.expected = expected
        
        context = context or {}
        if input_name:
            context["input_name"] = input_name
        if input_value is not None:
            context["input_value"] = input_value
        if expected is not None:
            context["expected"] = expected
        
        if input_name:
            if input_value is not None and expected is not None:
                message = f"Invalid input '{input_name}': {message}. Got '{input_value}', expected {expected}"
            elif input_value is not None:
                message = f"Invalid input '{input_name}': {message}. Got '{input_value}'"
            else:
                message = f"Invalid input '{input_name}': {message}"
                
        super().__init__(message, model_name, context)


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
        timeout_seconds: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with timeout error details.
        
        Args:
            message: Error message describing the timeout issue
            model_name: Optional name of the model
            image_path: Optional path of the image being processed
            timeout_seconds: Optional timeout threshold in seconds
            context: Optional dictionary with additional error context
        """
        self.timeout_seconds = timeout_seconds
        
        context = context or {}
        if timeout_seconds is not None:
            context["timeout_seconds"] = timeout_seconds
            
        timeout_info = f" after {timeout_seconds:.1f}s" if timeout_seconds else ""
        message = f"Timeout{timeout_info}: {message}"
        
        super().__init__(message, model_name, image_path, "inference", context)


class ModelLoaderTimeoutError(ModelInitializationError):
    """
    Raised when model loading exceeds time limits.
    
    This exception indicates issues with:
    - Model weight loading taking too long
    - Resource allocation delays
    - Network or disk I/O bottlenecks
    - External service dependencies
    """
    
    def __init__(
        self, 
        message: str, 
        model_name: Optional[str] = None,
        component: Optional[str] = None,
        resource_name: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with loader timeout details.
        
        Args:
            message: Error message describing the timeout issue
            model_name: Optional name of the model
            component: Optional component where loading timed out
            resource_name: Optional name of the resource being loaded
            timeout_seconds: Optional timeout threshold in seconds
            context: Optional dictionary with additional error context
        """
        self.resource_name = resource_name
        self.timeout_seconds = timeout_seconds
        
        context = context or {}
        if resource_name:
            context["resource_name"] = resource_name
        if timeout_seconds is not None:
            context["timeout_seconds"] = timeout_seconds
        
        resource_info = f" resource '{resource_name}'" if resource_name else ""
        timeout_info = f" after {timeout_seconds:.1f}s" if timeout_seconds else ""
        
        error_message = f"Loading{resource_info} timed out{timeout_info}: {message}"
        super().__init__(error_message, model_name, component, context)


class ModelCreationError(ModelError):
    """
    Raised when model creation fails in the factory.
    
    This exception indicates issues with:
    - Unsupported model types
    - Factory configuration
    - Implementation registration
    """
    
    def __init__(
        self, 
        message: str, 
        model_name: Optional[str] = None,
        model_type: Optional[str] = None,
        cause: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with creation error details.
        
        Args:
            message: Error message describing the creation issue
            model_name: Optional name of the model
            model_type: Optional type of model being created
            cause: Optional exception that caused this error
            context: Optional dictionary with additional error context
        """
        self.model_type = model_type
        self.cause = cause
        
        context = context or {}
        if model_type:
            context["model_type"] = model_type
        if cause:
            context["cause"] = str(cause)
        
        type_info = f" of type '{model_type}'" if model_type else ""
        super().__init__(f"Creation failed{type_info}: {message}", model_name, context) 