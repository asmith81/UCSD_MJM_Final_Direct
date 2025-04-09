"""
Error Recovery for Model Operations.

This module provides utilities for recovering from errors during model operations,
ensuring proper resource cleanup and state management.
"""
import contextlib
import functools
import logging
import sys
import traceback
from typing import Any, Callable, Dict, List, Optional, TypeVar, cast

from .model_errors import ModelError, ModelResourceError
from .model_resource_manager import ModelResourceManager

# Set up logger for this module
logger = logging.getLogger(__name__)

# Type variable for generic function return type
T = TypeVar('T')


class ErrorRecoveryManager:
    """
    Manages error recovery for model operations.
    
    This class provides utilities for:
    - Capturing detailed error context
    - Ensuring resource cleanup on errors
    - Logging errors with proper context
    - Managing recovery actions
    """
    
    def __init__(
        self, 
        resource_manager: Optional[ModelResourceManager] = None,
        model_name: Optional[str] = None
    ):
        """
        Initialize the error recovery manager.
        
        Args:
            resource_manager: Optional resource manager for resource cleanup
            model_name: Optional model name for error context
        """
        self.resource_manager = resource_manager
        self.model_name = model_name
        self._recovery_actions: List[Callable[[], None]] = []
        
    def register_recovery_action(self, action: Callable[[], None]) -> None:
        """
        Register an action to be executed during recovery.
        
        Actions will be called in reverse order of registration (LIFO).
        
        Args:
            action: Function to call during recovery
        """
        self._recovery_actions.append(action)
        
    def execute_recovery(self) -> None:
        """
        Execute all registered recovery actions.
        
        Actions are executed in reverse order (LIFO) and exceptions
        during recovery are logged but do not prevent other actions.
        """
        # Execute recovery actions in reverse order (LIFO)
        for action in reversed(self._recovery_actions):
            try:
                action()
            except Exception as e:
                logger.error(f"Error during recovery action: {str(e)}")
        
        # Clear recovery actions after execution
        self._recovery_actions.clear()
        
        # Clean up resources if resource manager is available
        if self.resource_manager:
            try:
                self.resource_manager.close_all()
            except Exception as e:
                logger.error(f"Error during resource cleanup: {str(e)}")
    
    def get_error_context(self, exception: Exception) -> Dict[str, Any]:
        """
        Get detailed context information for an error.
        
        Args:
            exception: The exception to get context for
            
        Returns:
            Dictionary with error context information
        """
        # Start with basic context
        context = {}
        
        # Add traceback information
        tb = traceback.extract_tb(sys.exc_info()[2])
        if tb:
            context["error_file"] = tb[-1].filename
            context["error_line"] = tb[-1].lineno
            context["error_function"] = tb[-1].name
            
        # Add model name if available
        if self.model_name:
            context["model_name"] = self.model_name
            
        # Add exception details
        context["exception_type"] = type(exception).__name__
        context["exception_message"] = str(exception)
        
        # If it's a ModelError, merge its context
        if isinstance(exception, ModelError) and exception.context:
            context.update(exception.context)
            
        return context
    
    @contextlib.contextmanager
    def recovery_context(self, operation_name: str = "operation"):
        """
        Context manager for operations that need error recovery.
        
        This context manager will:
        - Execute recovery actions if an exception occurs
        - Log detailed error information
        - Re-raise the original exception
        
        Args:
            operation_name: Name of the operation for logging
            
        Yields:
            None
        """
        try:
            yield
        except Exception as e:
            # Get error context
            context = self.get_error_context(e)
            
            # Log the error with context
            logger.error(
                f"Error during {operation_name}: {type(e).__name__}: {str(e)}",
                extra={"error_context": context}
            )
            
            # Execute recovery actions
            self.execute_recovery()
            
            # Re-raise the original exception
            raise


def with_error_recovery(
    operation_name: Optional[str] = None,
    resource_manager: Optional[ModelResourceManager] = None,
    model_name: Optional[str] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for functions that need error recovery.
    
    Args:
        operation_name: Name of the operation for logging
        resource_manager: Optional resource manager for cleanup
        model_name: Optional model name for error context
        
    Returns:
        Function decorator that adds error recovery
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Use function name as operation name if not provided
        func_operation_name = operation_name or func.__name__
        
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Create recovery manager
            recovery_manager = ErrorRecoveryManager(resource_manager, model_name)
            
            # Execute with recovery context
            with recovery_manager.recovery_context(func_operation_name):
                return func(*args, **kwargs)
                
        return wrapper
    
    return decorator 