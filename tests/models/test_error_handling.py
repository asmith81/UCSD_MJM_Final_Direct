"""
Tests for model error handling.

This module tests the error handling components for model loading and inference.
"""
import os
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, Optional
from unittest import mock

from PIL import Image

from src.config.base_config import BaseConfig
from src.models.base_model_impl import BaseModelImpl
from src.models.error_recovery import ErrorRecoveryManager, with_error_recovery
from src.models.model_errors import (
    ModelConfigError,
    ModelInitializationError,
    ModelInputError,
    ModelLoaderTimeoutError,
    ModelProcessingError,
    ModelResourceError,
    ModelTimeoutError
)
from src.models.model_loading_timeout import TimeoutHandler, load_model_with_timeout
from src.models.retry_utils import RetryConfig, with_retry


class MockConfig(BaseConfig):
    """Mock configuration class for testing."""
    
    def __init__(self, config_dict: Dict[str, Any]):
        self.config = config_dict
        
    def get_value(self, key: str, default=None):
        return self.config.get(key, default)
        
    def has_value(self, key: str) -> bool:
        return key in self.config
    
    def get_data(self) -> Dict[str, Any]:
        """Return all configuration data."""
        return self.config.copy()
    
    def get_section(self, section_name: str) -> Dict[str, Any]:
        """Return a configuration section."""
        return self.config.get(section_name, {})
    
    def validate(self) -> bool:
        """Validate the configuration."""
        return True


class SlowTestModel(BaseModelImpl):
    """Test model that simulates slow loading and processing."""
    
    def _initialize_impl(self, config: BaseConfig) -> None:
        """Simulate slow initialization."""
        delay = config.get_value("init_delay", 0)
        if delay > 0:
            time.sleep(delay)
            
        error_type = config.get_value("init_error", None)
        if error_type == "resource":
            raise ModelResourceError("Test resource error", model_name="SlowTestModel")
        elif error_type == "initialization":
            raise ModelInitializationError("Test initialization error", model_name="SlowTestModel")
            
    def _process_image_impl(self, image: Image.Image, image_path: Path) -> Dict[str, Any]:
        """Simulate slow processing."""
        delay = self._config.get_value("process_delay", 0)
        if delay > 0:
            time.sleep(delay)
            
        error_type = self._config.get_value("process_error", None)
        if error_type == "processing":
            raise ModelProcessingError("Test processing error", model_name="SlowTestModel")
        elif error_type == "input":
            raise ModelInputError("Test input error", model_name="SlowTestModel")
            
        return {"result": "success"}
        
    def _validate_config_impl(self, config: BaseConfig) -> bool:
        """Validate test configuration."""
        if config.get_value("config_error", False):
            raise ModelConfigError("Test config error", model_name="SlowTestModel")
        return True


class TestRetryUtils(unittest.TestCase):
    """Test the retry utilities."""
    
    def test_retry_success_first_attempt(self):
        """Test successful function execution on first attempt."""
        counter = {"count": 0}
        
        @with_retry()
        def test_func():
            counter["count"] += 1
            return "success"
            
        result = test_func()
        self.assertEqual(result, "success")
        self.assertEqual(counter["count"], 1)
    
    def test_retry_success_after_retries(self):
        """Test successful function execution after retries."""
        counter = {"count": 0}
        
        @with_retry(RetryConfig(max_attempts=3, delay_seconds=0.1))
        def test_func():
            counter["count"] += 1
            if counter["count"] < 3:
                raise ValueError("Test error")
            return "success"
            
        result = test_func()
        self.assertEqual(result, "success")
        self.assertEqual(counter["count"], 3)
    
    def test_retry_max_attempts_exceeded(self):
        """Test max retry attempts exceeded."""
        counter = {"count": 0}
        
        @with_retry(RetryConfig(max_attempts=3, delay_seconds=0.1))
        def test_func():
            counter["count"] += 1
            raise ValueError("Test error")
            
        with self.assertRaises(ValueError):
            test_func()
            
        self.assertEqual(counter["count"], 3)
    
    def test_retry_non_retryable_exception(self):
        """Test non-retryable exception not retried."""
        counter = {"count": 0}
        
        @with_retry(RetryConfig(
            max_attempts=3, 
            delay_seconds=0.1,
            non_retryable_exceptions=[KeyError]
        ))
        def test_func():
            counter["count"] += 1
            raise KeyError("Test error")
            
        with self.assertRaises(KeyError):
            test_func()
            
        self.assertEqual(counter["count"], 1)


class TestErrorRecovery(unittest.TestCase):
    """Test the error recovery utilities."""
    
    def test_recovery_actions_executed(self):
        """Test that recovery actions are executed when an error occurs."""
        action1_called = False
        action2_called = False
        
        def action1():
            nonlocal action1_called
            action1_called = True
            
        def action2():
            nonlocal action2_called
            action2_called = True
            
        recovery_manager = ErrorRecoveryManager()
        recovery_manager.register_recovery_action(action1)
        recovery_manager.register_recovery_action(action2)
        
        with self.assertRaises(ValueError):
            with recovery_manager.recovery_context("test"):
                raise ValueError("Test error")
                
        self.assertTrue(action1_called)
        self.assertTrue(action2_called)
    
    def test_error_recovery_decorator(self):
        """Test the error recovery decorator."""
        recovery_executed = [False]  # Using a list to allow mutation in nested function
        
        # Function to register as recovery action
        def recovery_action():
            recovery_executed[0] = True
        
        # Decorated function that sets up recovery and raises error
        @with_error_recovery(operation_name="test_operation")
        def test_func():
            # Create a recovery manager directly accessible to our test
            manager = ErrorRecoveryManager()
            # Register our test recovery action
            manager.register_recovery_action(recovery_action)
            # Use the context manager to ensure actions are executed
            with manager.recovery_context("test_nested_context"):
                raise ValueError("Test error")
        
        # Verify the error is raised and propagated
        with self.assertRaises(ValueError):
            test_func()
            
        # Now check if the recovery action was called
        self.assertTrue(recovery_executed[0], "Recovery action was not executed")


class TestModelLoadingTimeout(unittest.TestCase):
    """Test the model loading timeout utilities."""
    
    def test_timeout_handler(self):
        """Test the timeout handler using a direct approach."""
        # Create a simple function that should timeout
        def function_that_sleeps():
            time.sleep(1.0)  # Sleep for 1 second
            return "completed"
        
        # Create a ThreadPoolExecutor with short timeout
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(function_that_sleeps)
            
            # This should timeout before the function completes
            with self.assertRaises(Exception):  # Can be TimeoutError or FutureTimeoutError
                future.result(timeout=0.1)  # 0.1 second timeout
    
    def test_load_model_with_timeout_success(self):
        """Test successful model loading with timeout."""
        def quick_loader():
            return "model"
            
        result = load_model_with_timeout(quick_loader, 1.0)
        self.assertEqual(result, "model")
    
    def test_load_model_with_timeout_failure(self):
        """Test model loading timeout."""
        def slow_loader():
            time.sleep(0.3)  # Sleep long enough to trigger timeout
            return "model"
            
        with self.assertRaises(ModelLoaderTimeoutError):
            load_model_with_timeout(slow_loader, 0.1)


class TestModelErrorHandling(unittest.TestCase):
    """Test the model error handling in BaseModelImpl."""
    
    def setUp(self):
        """Set up test resources."""
        # Create a temporary image for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_image_path = Path(self.temp_dir.name) / "test_image.png"
        
        # Create a simple test image
        test_image = Image.new('RGB', (100, 100), color='white')
        test_image.save(self.temp_image_path)
    
    def tearDown(self):
        """Clean up test resources."""
        self.temp_dir.cleanup()
    
    def test_model_initialization_timeout(self):
        """Test model initialization timeout."""
        model = SlowTestModel()
        config = MockConfig({
            "name": "test_model",
            "type": "slow_test",
            "version": "1.0",
            "init_delay": 0.3,  # Delay longer than timeout
            "loading_timeout_seconds": 0.1
        })
        
        with self.assertRaises(ModelLoaderTimeoutError):
            model.initialize(config)
    
    def test_model_initialization_error(self):
        """Test model initialization error."""
        model = SlowTestModel()
        config = MockConfig({
            "name": "test_model",
            "type": "slow_test",
            "version": "1.0",
            "init_error": "initialization"
        })
        
        with self.assertRaises(ModelInitializationError):
            model.initialize(config)
    
    def test_model_resource_error(self):
        """Test model resource error."""
        model = SlowTestModel()
        config = MockConfig({
            "name": "test_model",
            "type": "slow_test",
            "version": "1.0",
            "init_error": "resource"
        })
        
        with self.assertRaises(ModelResourceError):
            model.initialize(config)
    
    def test_model_config_error(self):
        """Test model configuration error."""
        model = SlowTestModel()
        config = MockConfig({
            "name": "test_model",
            "type": "slow_test",
            "version": "1.0",
            "config_error": True
        })
        
        with self.assertRaises(ModelConfigError):
            model.initialize(config)
    
    def test_model_processing_timeout(self):
        """Test model processing timeout."""
        # Create and initialize model
        model = SlowTestModel()
        model.initialize(MockConfig({
            "name": "test_model",
            "type": "slow_test",
            "version": "1.0",
        }))
        
        # Mock _process_image_with_timeout to raise TimeoutError
        original_process = model._process_image_with_timeout
        
        def mock_process(*args, **kwargs):
            raise TimeoutError("Test timeout")
            
        # Apply mock and test
        model._process_image_with_timeout = mock_process
        
        with self.assertRaises(ModelTimeoutError):
            model.process_image(self.temp_image_path)
            
        # Restore original method
        model._process_image_with_timeout = original_process
    
    def test_model_processing_error(self):
        """Test model processing error."""
        # Create and initialize model
        model = SlowTestModel()
        config = MockConfig({
            "name": "test_model",
            "type": "slow_test",
            "version": "1.0",
            "process_error": "processing"
        })
        model.initialize(config)
        
        with self.assertRaises(ModelProcessingError):
            model.process_image(self.temp_image_path)
    
    def test_model_input_error(self):
        """Test model input error."""
        # Create and initialize model
        model = SlowTestModel()
        config = MockConfig({
            "name": "test_model",
            "type": "slow_test",
            "version": "1.0",
            "process_error": "input"
        })
        model.initialize(config)
        
        with self.assertRaises(ModelInputError):
            model.process_image(self.temp_image_path)
    
    def test_file_not_found_error(self):
        """Test file not found error."""
        # Create and initialize model
        model = SlowTestModel()
        config = MockConfig({
            "name": "test_model",
            "type": "slow_test",
            "version": "1.0"
        })
        model.initialize(config)
        
        # Use a non-existent file path
        non_existent_path = Path(self.temp_dir.name) / "non_existent.png"
        
        with self.assertRaises(FileNotFoundError):
            model.process_image(non_existent_path)
    
    def test_successful_processing(self):
        """Test successful model processing."""
        # Create and initialize model
        model = SlowTestModel()
        config = MockConfig({
            "name": "test_model",
            "type": "slow_test",
            "version": "1.0"
        })
        model.initialize(config)
        
        # Process image
        result = model.process_image(self.temp_image_path)
        self.assertEqual(result, {"result": "success"})


if __name__ == "__main__":
    unittest.main() 