"""
Retry Utilities for Model Operations.

This module provides utilities for retrying operations that might experience
transient failures, with configurable retry policies and error handling.
"""
import functools
import logging
import time
from typing import Any, Callable, List, Optional, Type, TypeVar, Union, cast

from .model_errors import ModelError

# Set up logger for this module
logger = logging.getLogger(__name__)

# Type variable for the return type of functions to be retried
T = TypeVar('T')


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        delay_seconds: float = 1.0,
        backoff_factor: float = 2.0,
        max_delay_seconds: float = 30.0,
        retryable_exceptions: Optional[List[Type[Exception]]] = None,
        non_retryable_exceptions: Optional[List[Type[Exception]]] = None
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_attempts: Maximum number of attempts (including initial attempt)
            delay_seconds: Initial delay between attempts in seconds
            backoff_factor: Multiplier for delay after each attempt
            max_delay_seconds: Maximum delay between attempts in seconds
            retryable_exceptions: List of exception types that should trigger retry
            non_retryable_exceptions: List of exception types that should not trigger retry
        """
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if delay_seconds < 0:
            raise ValueError("delay_seconds must be non-negative")
        if backoff_factor < 1.0:
            raise ValueError("backoff_factor must be at least 1.0")
        if max_delay_seconds < delay_seconds:
            raise ValueError("max_delay_seconds must be at least delay_seconds")
            
        self.max_attempts = max_attempts
        self.delay_seconds = delay_seconds
        self.backoff_factor = backoff_factor
        self.max_delay_seconds = max_delay_seconds
        self.retryable_exceptions = retryable_exceptions or []
        self.non_retryable_exceptions = non_retryable_exceptions or []
        
    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """
        Determine if an operation should be retried based on the exception and attempt number.
        
        Args:
            exception: The exception that was raised
            attempt: Current attempt number (1-based)
            
        Returns:
            True if the operation should be retried, False otherwise
        """
        # Check if we've reached max attempts
        if attempt >= self.max_attempts:
            return False
        
        # Check if exception is in non-retryable list
        for exc_type in self.non_retryable_exceptions:
            if isinstance(exception, exc_type):
                return False
        
        # If retryable list is empty, retry all exceptions not in non-retryable list
        if not self.retryable_exceptions:
            return True
        
        # Check if exception is in retryable list
        for exc_type in self.retryable_exceptions:
            if isinstance(exception, exc_type):
                return True
                
        return False
    
    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay for a specific attempt.
        
        Args:
            attempt: Current attempt number (1-based)
            
        Returns:
            Delay in seconds
        """
        if attempt <= 1:
            return 0.0
            
        delay = self.delay_seconds * (self.backoff_factor ** (attempt - 2))
        return min(delay, self.max_delay_seconds)


def with_retry(
    config: Optional[RetryConfig] = None,
    logger: Optional[logging.Logger] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for retrying functions that may experience transient errors.
    
    Args:
        config: Retry configuration, or None to use defaults
        logger: Logger to use, or None to use module logger
        
    Returns:
        Function decorator that adds retry behavior
    """
    retry_config = config or RetryConfig()
    logger_to_use = logger or logging.getLogger(__name__)
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Optional[Exception] = None
            
            for attempt in range(1, retry_config.max_attempts + 1):
                try:
                    # Attempt the operation
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    last_exception = e
                    
                    # Determine if we should retry
                    if not retry_config.should_retry(e, attempt):
                        logger_to_use.debug(
                            f"Not retrying {func.__name__} after attempt {attempt}: {str(e)}"
                        )
                        break
                    
                    # Calculate delay for next attempt
                    delay = retry_config.get_delay(attempt)
                    
                    # Log retry attempt
                    logger_to_use.info(
                        f"Retrying {func.__name__} after attempt {attempt} in {delay:.1f}s: {str(e)}"
                    )
                    
                    # Wait before next attempt
                    if delay > 0:
                        time.sleep(delay)
            
            # If we get here, all retries failed
            if last_exception is not None:
                # Enhance with retry context for ModelError types
                if isinstance(last_exception, ModelError) and last_exception.context is not None:
                    last_exception.context["retry_attempts"] = retry_config.max_attempts
                    
                logger_to_use.error(
                    f"All {retry_config.max_attempts} attempts of {func.__name__} failed"
                )
                raise last_exception
                
            # Should never get here, but for type safety
            raise RuntimeError(f"Unexpected error in retry logic for {func.__name__}")
            
        return wrapper
    
    return decorator


def create_retryable_function(
    func: Callable[..., T],
    config: Optional[RetryConfig] = None,
    logger: Optional[logging.Logger] = None
) -> Callable[..., T]:
    """
    Creates a retryable version of a function without modifying the original.
    
    Args:
        func: Function to make retryable
        config: Retry configuration, or None to use defaults
        logger: Logger to use, or None to use module logger
        
    Returns:
        A new function with retry behavior
    """
    decorator = with_retry(config, logger)
    return decorator(func) 