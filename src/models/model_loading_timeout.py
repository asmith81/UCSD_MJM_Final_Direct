"""
Model Loading Timeout Handler.

This module provides utilities for handling timeouts during model loading operations.
It ensures that model loading operations do not hang indefinitely.
"""
import contextlib
import logging
import signal
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from typing import Any, Callable, Optional, TypeVar, cast

from .model_errors import ModelLoaderTimeoutError

# Set up logger for this module
logger = logging.getLogger(__name__)

# Type variable for function return type
T = TypeVar('T')


class TimeoutHandler:
    """Handler for operations that might time out."""
    
    @staticmethod
    def _timeout_handler(signum: int, frame: Any) -> None:
        """Signal handler for timeout."""
        raise TimeoutError("Operation timed out")
    
    @staticmethod
    @contextlib.contextmanager
    def timeout(seconds: float, error_message: str = "Operation timed out"):
        """
        Context manager for timing out operations.
        
        This uses SIGALRM for timeout handling, which is only available on Unix systems.
        On Windows, this will fall back to a threaded implementation.
        
        Args:
            seconds: Timeout in seconds
            error_message: Custom error message for timeout
            
        Yields:
            None
            
        Raises:
            TimeoutError: If the operation times out
        """
        # Try to use SIGALRM if available (Unix-like systems)
        try:
            # Check if signal.SIGALRM is available
            if hasattr(signal, 'SIGALRM'):
                # Save previous handler
                previous_handler = signal.getsignal(signal.SIGALRM)
                
                # Set alarm handler
                signal.signal(signal.SIGALRM, TimeoutHandler._timeout_handler)
                
                try:
                    # Set alarm
                    signal.setitimer(signal.ITIMER_REAL, seconds)
                    yield
                finally:
                    # Cancel alarm and restore previous handler
                    signal.setitimer(signal.ITIMER_REAL, 0)
                    signal.signal(signal.SIGALRM, previous_handler)
            else:
                # Fall back to threaded implementation
                with TimeoutHandler.thread_timeout(seconds, error_message):
                    yield
        except Exception:
            # Fall back to threaded implementation if SIGALRM fails
            with TimeoutHandler.thread_timeout(seconds, error_message):
                yield
    
    @staticmethod
    @contextlib.contextmanager
    def thread_timeout(seconds: float, error_message: str = "Operation timed out"):
        """
        Context manager for timing out operations using threads.
        
        This implementation works on all platforms but may not be as reliable
        for certain types of operations.
        
        Args:
            seconds: Timeout in seconds
            error_message: Custom error message for timeout
            
        Yields:
            None
            
        Raises:
            TimeoutError: If the operation times out
        """
        # Event for signaling completion
        completion_event = threading.Event()
        
        # Thread for monitoring timeout
        def monitor_timeout() -> None:
            # Wait for completion with timeout
            if not completion_event.wait(seconds):
                # If event is not set, raise timeout in main thread
                # Note: This will raise the exception in the main thread's
                # exception stack, which will be caught by the context manager
                # when the main thread reaches the next Python bytecode
                raise TimeoutError(error_message)
        
        # Start monitor thread
        monitor_thread = threading.Thread(target=monitor_timeout)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        try:
            # Execute operation
            yield
            # Signal completion
            completion_event.set()
        finally:
            # Ensure completion is signaled even on exception
            completion_event.set()
            # Wait for monitor thread to complete
            monitor_thread.join(0.1)  # Short timeout to avoid hanging


def load_model_with_timeout(
    loader_func: Callable[[], T],
    timeout_seconds: float,
    model_name: Optional[str] = None,
    component: Optional[str] = None,
    resource_name: Optional[str] = None
) -> T:
    """
    Load a model with timeout using ThreadPoolExecutor.
    
    This function handles timeouts during model loading by executing the loader
    function in a separate thread and monitoring for timeout.
    
    Args:
        loader_func: Function that loads the model
        timeout_seconds: Timeout in seconds
        model_name: Optional model name for error context
        component: Optional component name for error context
        resource_name: Optional resource name for error context
        
    Returns:
        The loaded model
        
    Raises:
        ModelLoaderTimeoutError: If loading times out
        Any exception raised by the loader function
    """
    logger.debug(f"Loading model with {timeout_seconds}s timeout")
    
    # Record start time for accurate timeout reporting
    start_time = time.time()
    
    try:
        # Use ThreadPoolExecutor for timeout handling
        with ThreadPoolExecutor(max_workers=1) as executor:
            # Submit loading task to executor
            future = executor.submit(loader_func)
            
            try:
                # Wait for result with timeout
                return future.result(timeout=timeout_seconds)
            except FutureTimeoutError:
                # Calculate actual elapsed time
                elapsed = time.time() - start_time
                
                # Raise ModelLoaderTimeoutError with appropriate context
                raise ModelLoaderTimeoutError(
                    "Model loading operation exceeded time limit",
                    model_name=model_name,
                    component=component,
                    resource_name=resource_name,
                    timeout_seconds=elapsed
                )
    except ModelLoaderTimeoutError:
        # Re-raise ModelLoaderTimeoutError directly
        raise
    except Exception as e:
        # For other exceptions, log and re-raise
        logger.exception(f"Error loading model: {str(e)}")
        raise 