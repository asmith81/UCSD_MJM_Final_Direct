"""
Test the model resource manager.

This module tests the model resource manager to ensure
proper resource registration, tracking, and cleanup.
"""
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile
import os

from src.models.model_resource_manager import ModelResourceManager, ModelResource
from src.models.model_errors import ModelResourceError


class TestModelResource:
    """Test the ModelResource wrapper class."""
    
    def test_basic_resource_management(self):
        """Test basic resource creation and access."""
        resource = "test_resource"
        cleanup_fn = MagicMock()
        
        # Create resource wrapper
        wrapper = ModelResource(
            resource=resource,
            resource_type="test",
            resource_name="test1",
            cleanup_fn=cleanup_fn
        )
        
        # Check properties
        assert wrapper.resource == resource
        assert wrapper.resource_type == "test"
        assert wrapper.resource_name == "test1"
        
        # Check get method
        assert wrapper.get() == resource
        
        # Check cleanup
        wrapper.close()
        cleanup_fn.assert_called_once_with(resource)
        
        # Check double cleanup (should not call again)
        cleanup_fn.reset_mock()
        wrapper.close()
        cleanup_fn.assert_not_called()
    
    def test_context_manager(self):
        """Test ModelResource as context manager."""
        resource = "test_resource"
        cleanup_fn = MagicMock()
        
        # Use as context manager
        with ModelResource(
            resource=resource,
            resource_type="test",
            resource_name="test1",
            cleanup_fn=cleanup_fn
        ) as res:
            assert res == resource
            
        # Cleanup should be called on exit
        cleanup_fn.assert_called_once_with(resource)
    
    def test_already_closed_error(self):
        """Test error when accessing closed resource."""
        resource = "test_resource"
        wrapper = ModelResource(
            resource=resource,
            resource_type="test",
            resource_name="test1",
            cleanup_fn=lambda r: None
        )
        
        # Close the resource
        wrapper.close()
        
        # Attempt to get should raise error
        with pytest.raises(ModelResourceError) as excinfo:
            wrapper.get()
        
        assert "Resource has been closed" in str(excinfo.value)
        assert "test" in str(excinfo.value)
        assert "test1" in str(excinfo.value)
        
    def test_cleanup_error_handling(self):
        """Test handling of errors during cleanup."""
        resource = "test_resource"
        cleanup_fn = MagicMock(side_effect=RuntimeError("Cleanup failed"))
        
        wrapper = ModelResource(
            resource=resource,
            resource_type="test",
            resource_name="test1",
            cleanup_fn=cleanup_fn
        )
        
        # Cleanup should not raise error
        wrapper.close()
        cleanup_fn.assert_called_once_with(resource)


class TestModelResourceManager:
    """Test the ModelResourceManager class."""
    
    def test_resource_registration(self):
        """Test registering and retrieving resources."""
        manager = ModelResourceManager(model_name="test_model")
        resource = "test_resource"
        cleanup_fn = MagicMock()
        
        # Register resource
        wrapper = manager.register_resource(
            resource=resource,
            resource_type="test",
            resource_name="test1",
            cleanup_fn=cleanup_fn
        )
        
        # Get resource
        retrieved = manager.get_resource("test", "test1")
        assert retrieved is wrapper
        assert retrieved.get() == resource
        
        # Close specific resource
        manager.close_resource("test", "test1")
        cleanup_fn.assert_called_once_with(resource)
        
        # Resource should be closed but still retrievable
        assert retrieved._is_closed == True
        
    def test_duplicate_registration(self):
        """Test error on duplicate resource registration."""
        manager = ModelResourceManager()
        
        # Register first resource
        manager.register_resource(
            resource="resource1",
            resource_type="test",
            resource_name="test1"
        )
        
        # Attempt to register duplicate
        with pytest.raises(ModelResourceError) as excinfo:
            manager.register_resource(
                resource="resource2",
                resource_type="test",
                resource_name="test1"
            )
            
        assert "Resource already registered" in str(excinfo.value)
        
    def test_nonexistent_resource(self):
        """Test error when accessing nonexistent resource."""
        manager = ModelResourceManager()
        
        # Attempt to get nonexistent resource
        with pytest.raises(ModelResourceError) as excinfo:
            manager.get_resource("test", "nonexistent")
            
        assert "Resource not found" in str(excinfo.value)
        
        # Attempt to close nonexistent resource
        with pytest.raises(ModelResourceError):
            manager.close_resource("test", "nonexistent")
            
    def test_close_all(self):
        """Test closing all resources."""
        manager = ModelResourceManager()
        cleanup1 = MagicMock()
        cleanup2 = MagicMock()
        
        # Register multiple resources
        manager.register_resource(
            resource="resource1",
            resource_type="test",
            resource_name="test1",
            cleanup_fn=cleanup1
        )
        
        manager.register_resource(
            resource="resource2",
            resource_type="test",
            resource_name="test2",
            cleanup_fn=cleanup2
        )
        
        # Close all resources
        manager.close_all()
        
        # Both cleanups should be called
        cleanup1.assert_called_once_with("resource1")
        cleanup2.assert_called_once_with("resource2")
        
    def test_managed_resource(self):
        """Test managed_resource context manager."""
        manager = ModelResourceManager()
        cleanup_fn = MagicMock()
        creator_fn = MagicMock(return_value="created_resource")
        
        # Use managed_resource context manager
        with manager.managed_resource(
            resource_type="test",
            resource_name="managed1",
            creator_fn=creator_fn,
            cleanup_fn=cleanup_fn
        ) as resource:
            assert resource == "created_resource"
            
            # Resource should be registered
            wrapper = manager.get_resource("test", "managed1")
            assert wrapper.get() == "created_resource"
        
        # Resource should be closed after context
        cleanup_fn.assert_called_once_with("created_resource")
        
    def test_managed_resource_error(self):
        """Test error handling in managed_resource."""
        manager = ModelResourceManager()
        cleanup_fn = MagicMock()
        
        # Creator function that raises error
        def failing_creator():
            raise RuntimeError("Creation failed")
        
        # Use managed_resource with failing creator
        with pytest.raises(ModelResourceError) as excinfo:
            with manager.managed_resource(
                resource_type="test",
                resource_name="will_fail",
                creator_fn=failing_creator,
                cleanup_fn=cleanup_fn
            ):
                pass
                
        assert "Failed to create or use resource" in str(excinfo.value)
        assert "Creation failed" in str(excinfo.value)
        cleanup_fn.assert_not_called()  # Nothing to clean up
        
    def test_managed_resource_usage_error(self):
        """Test error handling for errors during resource usage."""
        manager = ModelResourceManager()
        cleanup_fn = MagicMock()
        
        # Use managed_resource with error during usage
        with pytest.raises(ModelResourceError) as excinfo:
            with manager.managed_resource(
                resource_type="test",
                resource_name="will_be_used",
                creator_fn=lambda: "test_resource",
                cleanup_fn=cleanup_fn
            ) as resource:
                assert resource == "test_resource"
                raise RuntimeError("Usage error")
                
        # Check that the ModelResourceError contains the original error message
        assert "Failed to create or use resource" in str(excinfo.value)
        assert "Usage error" in str(excinfo.value)
        # Check that the resource info is included
        assert "test" in str(excinfo.value)
        assert "will_be_used" in str(excinfo.value)
        
        # Cleanup should be called exactly twice:
        # 1. In the managed_resource finally block
        # 2. When the ModelResource is closed in the context manager exit
        assert cleanup_fn.call_count == 2
        assert cleanup_fn.call_args_list == [
            ((("test_resource",)), {}),
            ((("test_resource",)), {})
        ]
        
    def test_open_file(self):
        """Test open_file resource manager."""
        manager = ModelResourceManager()
        
        # Create temporary file for testing
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp.write(b"test content")
            temp_path = Path(temp.name)
        
        try:
            # Use open_file context manager
            with manager.open_file(temp_path, "rb") as f:
                content = f.read()
                assert content == b"test content"
                
            # File should be closed after context
            assert f.closed
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    def test_open_nonexistent_file(self):
        """Test error handling for nonexistent file."""
        manager = ModelResourceManager()
        nonexistent_path = Path("nonexistent_file.txt")
        
        # Attempt to open nonexistent file
        with pytest.raises(ModelResourceError) as excinfo:
            with manager.open_file(nonexistent_path):
                pass
                
        assert "Cannot open file" in str(excinfo.value)
        assert "No such file or directory" in str(excinfo.value) 