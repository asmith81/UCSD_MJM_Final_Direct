"""
Model Resource Manager.

This module provides utilities for managing model resources
and ensuring proper cleanup when errors occur.
"""
import logging
import contextlib
from pathlib import Path
from typing import Any, Optional, Dict, Callable, TypeVar, Generator, Generic

from .model_errors import ModelResourceError

# Set up logger for this module
logger = logging.getLogger(__name__)

# Type variables for resource manager
T = TypeVar('T')
R = TypeVar('R')


class ModelResource(Generic[T]):
    """
    Represents a managed resource for model operations.
    
    This class wraps a resource and ensures proper cleanup when the resource
    is no longer needed or when errors occur during resource usage.
    """
    
    def __init__(
        self, 
        resource: T,
        resource_type: str,
        resource_name: str,
        cleanup_fn: Optional[Callable[[T], None]] = None
    ):
        """
        Initialize the resource wrapper.
        
        Args:
            resource: The actual resource being managed
            resource_type: Type description of the resource (e.g., "file", "model weights")
            resource_name: Name or identifier for the resource
            cleanup_fn: Optional function to call for cleanup when done
        """
        self.resource = resource
        self.resource_type = resource_type
        self.resource_name = resource_name
        self._cleanup_fn = cleanup_fn
        self._is_closed = False
        
    def get(self) -> T:
        """
        Get the managed resource.
        
        Returns:
            The managed resource
            
        Raises:
            ModelResourceError: If resource has already been closed
        """
        if self._is_closed:
            raise ModelResourceError(
                "Resource has been closed",
                resource_type=self.resource_type,
                resource_name=self.resource_name
            )
        return self.resource
    
    def close(self) -> None:
        """
        Close the resource, performing any necessary cleanup.
        Does nothing if resource is already closed.
        """
        if not self._is_closed and self._cleanup_fn is not None:
            try:
                self._cleanup_fn(self.resource)
                logger.debug(f"Closed resource {self.resource_type}: {self.resource_name}")
            except Exception as e:
                logger.warning(
                    f"Error during resource cleanup for {self.resource_type} '{self.resource_name}': {str(e)}"
                )
            self._is_closed = True
    
    def __enter__(self) -> T:
        """Context manager entry - returns the resource."""
        return self.get()
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - closes the resource."""
        self.close()


class ModelResourceManager:
    """
    Manages resources for model operations.
    
    This class helps track and clean up resources used during model
    initialization and inference, ensuring proper cleanup on errors.
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the resource manager.
        
        Args:
            model_name: Optional name of the model using this manager
        """
        self.model_name = model_name
        self._resources: Dict[str, ModelResource] = {}
        
    def register_resource(
        self,
        resource: Any,
        resource_type: str,
        resource_name: str,
        cleanup_fn: Optional[Callable[[Any], None]] = None
    ) -> ModelResource:
        """
        Register a resource to be managed.
        
        Args:
            resource: The resource to manage
            resource_type: Type of resource being managed
            resource_name: Name/identifier for the resource
            cleanup_fn: Optional function to call for cleanup
            
        Returns:
            ModelResource: Managed resource wrapper
            
        Raises:
            ModelResourceError: If a resource with same name/type already exists
        """
        key = f"{resource_type}:{resource_name}"
        if key in self._resources:
            raise ModelResourceError(
                f"Resource already registered",
                model_name=self.model_name,
                resource_type=resource_type,
                resource_name=resource_name
            )
            
        resource_wrapper = ModelResource(
            resource=resource,
            resource_type=resource_type,
            resource_name=resource_name,
            cleanup_fn=cleanup_fn
        )
        self._resources[key] = resource_wrapper
        logger.debug(f"Registered resource {resource_type}: {resource_name}")
        return resource_wrapper
    
    def get_resource(self, resource_type: str, resource_name: str) -> ModelResource:
        """
        Retrieve a managed resource.
        
        Args:
            resource_type: Type of resource to retrieve
            resource_name: Name of resource to retrieve
            
        Returns:
            ModelResource: The managed resource wrapper
            
        Raises:
            ModelResourceError: If resource doesn't exist
        """
        key = f"{resource_type}:{resource_name}"
        if key not in self._resources:
            raise ModelResourceError(
                f"Resource not found",
                model_name=self.model_name,
                resource_type=resource_type,
                resource_name=resource_name
            )
        return self._resources[key]
    
    def close_resource(self, resource_type: str, resource_name: str) -> None:
        """
        Close a specific resource.
        
        Args:
            resource_type: Type of resource to close
            resource_name: Name of resource to close
            
        Raises:
            ModelResourceError: If resource doesn't exist
        """
        resource = self.get_resource(resource_type, resource_name)
        resource.close()
        
    def close_all(self) -> None:
        """Close all managed resources."""
        for key, resource in list(self._resources.items()):
            try:
                resource.close()
            except Exception as e:
                logger.warning(f"Error closing resource {key}: {str(e)}")
                
    def __del__(self) -> None:
        """Ensure resources are cleaned up when manager is garbage collected."""
        self.close_all()
        
    @contextlib.contextmanager
    def managed_resource(
        self,
        resource_type: str,
        resource_name: str,
        creator_fn: Callable[[], R],
        cleanup_fn: Optional[Callable[[R], None]] = None
    ) -> Generator[R, None, None]:
        """
        Context manager for resource lifecycle management.
        
        Creates a resource, registers it, and ensures cleanup when done or if errors occur.
        
        Args:
            resource_type: Type of resource to create
            resource_name: Name for the resource
            creator_fn: Function that creates the resource
            cleanup_fn: Optional function to clean up the resource
            
        Yields:
            The created resource
            
        Raises:
            ModelResourceError: If resource creation fails
        """
        resource = None
        try:
            # Create resource
            resource = creator_fn()
            
            # Register resource
            wrapper = self.register_resource(
                resource=resource,
                resource_type=resource_type,
                resource_name=resource_name,
                cleanup_fn=cleanup_fn
            )
            
            # Yield the resource
            yield resource
            
        except Exception as e:
            # Clean up if creation or registration fails
            if resource is not None and cleanup_fn is not None:
                try:
                    cleanup_fn(resource)
                except Exception as cleanup_e:
                    logger.warning(
                        f"Error during emergency resource cleanup for {resource_type} "
                        f"'{resource_name}': {str(cleanup_e)}"
                    )
            
            if isinstance(e, ModelResourceError):
                raise
                
            raise ModelResourceError(
                f"Failed to create or use resource: {str(e)}",
                model_name=self.model_name,
                resource_type=resource_type,
                resource_name=resource_name
            ) from e
            
        finally:
            # Always attempt to close the resource when done
            key = f"{resource_type}:{resource_name}"
            if key in self._resources:
                try:
                    self._resources[key].close()
                except Exception as e:
                    logger.warning(f"Error closing resource {key} in finally block: {str(e)}")
                    
    @contextlib.contextmanager
    def open_file(self, file_path: Path, mode: str = 'rb') -> Generator[Any, None, None]:
        """
        Open a file as a managed resource.
        
        Args:
            file_path: Path to the file
            mode: File open mode
            
        Yields:
            The opened file object
            
        Raises:
            ModelResourceError: If file cannot be opened
        """
        def opener():
            try:
                return open(file_path, mode)
            except (FileNotFoundError, PermissionError, IOError) as e:
                raise ModelResourceError(
                    f"Cannot open file: {str(e)}",
                    model_name=self.model_name,
                    resource_type="file",
                    resource_name=str(file_path)
                ) from e
                
        with self.managed_resource(
            resource_type="file",
            resource_name=str(file_path),
            creator_fn=opener,
            cleanup_fn=lambda f: f.close()
        ) as file_obj:
            yield file_obj 