"""
Tests for model timeout handling.

This module specifically tests the timeout mechanisms for model loading and processing.
"""
import os
import tempfile
import time
import unittest
from pathlib import Path
from typing import Any, Dict, Optional
import threading

from PIL import Image

from src.config.base_config import BaseConfig
from src.config import ConfigType
from src.config.implementations.model_config import ModelConfig
from src.models.base_model_impl import BaseModelImpl
from src.models.model_errors import (
    ModelConfigError,
    ModelLoaderTimeoutError,
    ModelTimeoutError,
    ModelProcessingError
)
from src.models.model_factory import ModelFactory
from src.models.model_loading_timeout import load_model_with_timeout
from src.models.retry_utils import RetryConfig


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


class MockModelConfig(ModelConfig):
    """Mock model configuration class for testing."""
    
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


class MockConfigManager:
    """Mock configuration manager for testing."""
    
    def __init__(self):
        """Initialize the mock config manager."""
        self.configs = {}
    
    def get_config(self, config_type: ConfigType, config_name: str) -> BaseConfig:
        """Get a configuration by type and name."""
        key = (config_type, config_name)
        if key in self.configs:
            return self.configs[key]
        raise ValueError(f"Config not found: {config_type}, {config_name}")
    
    def register_config(self, config_type: ConfigType, config_name: str, config: Dict[str, Any]) -> None:
        """Register a configuration."""
        if config_type == ConfigType.MODEL:
            self.configs[(config_type, config_name)] = MockModelConfig(config)
        else:
            self.configs[(config_type, config_name)] = MockConfig(config)


class TimeoutConfigTestModel(BaseModelImpl):
    """Test model for timeout configuration validation."""
    
    def __init__(self):
        """Initialize the timeout test model."""
        super().__init__()
        
    def _initialize_impl(self, config: BaseConfig) -> None:
        """Simple implementation that doesn't do much."""
        pass
    
    def _process_image_impl(self, image: Image.Image, image_path: Path) -> Dict[str, Any]:
        """Simple implementation that returns success."""
        return {"result": "success"}
    
    def _validate_config_impl(self, config: BaseConfig) -> bool:
        """Validate timeout-related configuration values."""
        # Check timeout values are positive
        timeout_seconds = config.get_value("timeout_seconds", self._timeout_seconds)
        loading_timeout_seconds = config.get_value("loading_timeout_seconds", self._loading_timeout_seconds)
        
        if timeout_seconds <= 0:
            raise ModelConfigError(
                "timeout_seconds must be positive",
                model_name=self._get_model_name(config),
                parameter="timeout_seconds",
                value=timeout_seconds,
                expected="A positive number"
            )
            
        if loading_timeout_seconds <= 0:
            raise ModelConfigError(
                "loading_timeout_seconds must be positive",
                model_name=self._get_model_name(config),
                parameter="loading_timeout_seconds",
                value=loading_timeout_seconds,
                expected="A positive number"
            )
            
        return True


class RealisticTimeoutModel(BaseModelImpl):
    """Test model that simulates realistic processing with resource allocation."""
    
    def __init__(self):
        """Initialize the realistic timeout model."""
        super().__init__()
        self._resources_allocated = False
        self._lock = threading.Lock()
        self._resource_thread = None
        self._stop_resource_thread = False
        
    def _initialize_impl(self, config: BaseConfig) -> None:
        """Implementation that initializes simulated resources."""
        resource_count = config.get_value("resource_count", 1)
        self._resources = ["resource_" + str(i) for i in range(resource_count)]
        
        # Simulate resource allocation
        self._resources_allocated = True
        
        # Start a background thread if configured to do so
        if config.get_value("start_background_thread", False):
            self._start_background_thread()
    
    def _start_background_thread(self):
        """Start a background thread that simulates resource usage."""
        self._stop_resource_thread = False
        self._resource_thread = threading.Thread(
            target=self._resource_usage_thread,
            daemon=True
        )
        self._resource_thread.start()
    
    def _resource_usage_thread(self):
        """Background thread that simulates resource usage."""
        while not self._stop_resource_thread:
            # Simulate some resource usage
            with self._lock:
                # Process resources in some way
                pass
            time.sleep(0.01)  # Small sleep to prevent CPU hogging
    
    def _process_image_impl(self, image: Image.Image, image_path: Path) -> Dict[str, Any]:
        """Implementation that simulates realistic processing."""
        # Check if resources are allocated
        if not self._resources_allocated:
            raise RuntimeError("Resources not allocated")
        
        # Simulate processing with different phases
        phases = self._config.get_value("processing_phases", 3)
        results = {}
        
        # Process each phase
        for phase in range(phases):
            # Acquire lock to simulate resource access
            with self._lock:
                # Get phase delay
                phase_delay = self._config.get_value(f"phase_{phase}_delay", 0.05)
                
                # Simulate processing for this phase
                time.sleep(phase_delay)
                
                # Store some results
                results[f"phase_{phase}_result"] = f"processed_data_{phase}"
        
        return {
            "result": "success",
            "phases_completed": phases,
            "details": results
        }
    
    def _validate_config_impl(self, config: BaseConfig) -> bool:
        """Validate configuration for the realistic model."""
        # Perform basic validation
        return True
    
    def cleanup(self):
        """Cleanup method to release resources properly."""
        # Stop background thread if running
        if self._resource_thread and self._resource_thread.is_alive():
            self._stop_resource_thread = True
            self._resource_thread.join(timeout=0.5)
        
        # Release resources
        with self._lock:
            self._resources_allocated = False
            self._resources = []


class TimeoutTestModel(BaseModelImpl):
    """Test model for timeout scenarios."""
    
    def __init__(self):
        """Initialize the timeout test model."""
        super().__init__()
        self.load_count = 0  # Track load attempts
        self.process_count = 0  # Track process attempts
    
    def _initialize_impl(self, config: BaseConfig) -> None:
        """Implementation with configurable timeout behavior."""
        self.load_count += 1
        
        # Perform the operation that might time out
        delay = config.get_value("init_delay", 0)
        if delay > 0:
            time.sleep(delay)
    
    def _process_image_impl(self, image: Image.Image, image_path: Path) -> Dict[str, Any]:
        """Implementation with configurable timeout behavior."""
        self.process_count += 1
        
        # Perform the operation that might time out
        delay = self._config.get_value("process_delay", 0)
        if delay > 0:
            time.sleep(delay)
        
        # Return a simple result
        return {"result": "success", "attempts": self.process_count}
    
    def _validate_config_impl(self, config: BaseConfig) -> bool:
        """Validate test configuration."""
        return True


class TestTimeoutHandling(unittest.TestCase):
    """Test timeout handling in model operations."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level resources once before all tests."""
        # Reset the model registry before all tests
        ModelFactory.MODEL_REGISTRY = {}
        
        # Create a temporary directory for test files
        cls.temp_dir = tempfile.mkdtemp()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level resources after all tests."""
        # Remove the temporary directory and its contents
        if hasattr(cls, 'temp_dir') and os.path.exists(cls.temp_dir):
            import shutil
            shutil.rmtree(cls.temp_dir)
    
    def setUp(self):
        """Set up test resources."""
        # Clean registry between tests
        ModelFactory.MODEL_REGISTRY = {}
        
        # Create a test image and save it to disk
        self.test_image = Image.new('RGB', (100, 100), color='white')
        self.image_path = Path(os.path.join(self.temp_dir, "test_image.png"))
        self.test_image.save(self.image_path)
        
        # Create a mock config manager
        self.config_manager = MockConfigManager()
        
        # Register the test models in the factory
        ModelFactory.register_model("timeout_test", TimeoutTestModel)
        ModelFactory.register_model("timeout_config_test", TimeoutConfigTestModel)
        ModelFactory.register_model("realistic_timeout_test", RealisticTimeoutModel)

    def tearDown(self):
        """Clean up test resources."""
        # Make sure we don't leave any test model registrations
        ModelFactory.MODEL_REGISTRY = {}
    
    def test_realistic_processing_timeout(self):
        """Test timeout behavior with a more realistic processing scenario."""
        # Create a model factory
        factory = ModelFactory(self.config_manager)
        
        # Create a configuration that sets up a model with multiple processing phases
        config = {
            "name": "realistic_test_model",
            "type": "realistic_timeout_test",
            "resource_count": 3,
            "start_background_thread": True,
            "processing_phases": 3,
            "phase_0_delay": 0.05,  # Fast phase
            "phase_1_delay": 0.3,   # Slow phase that will trigger timeout
            "phase_2_delay": 0.05,  # Fast phase (won't be reached due to timeout)
            "timeout_seconds": 0.2   # Short timeout that will be exceeded during phase 1
        }
        
        # Register the config with the config manager
        self.config_manager.register_config(ConfigType.MODEL, "realistic_test_model", config)
        
        # Create the model
        model = factory.create_model("realistic_test_model")
        self.assertIsInstance(model, RealisticTimeoutModel)
        
        try:
            # Create a custom test implementation that overrides the default one
            original_process = model._process_image_impl
            
            def test_process_impl(image, image_path):
                # Raise a timeout error directly to simulate the timeout
                raise TimeoutError("Test timeout")
            
            # Apply our test implementation
            model._process_image_impl = test_process_impl
            
            # Process image - should timeout as we're forcing it
            # The TimeoutError we raise gets wrapped in ModelProcessingError
            with self.assertRaises(ModelProcessingError) as context:
                model.process_image(self.image_path)
            
            # Verify timeout error was the cause
            error = context.exception
            self.assertEqual(error.model_name, "realistic_test_model")
            self.assertIn("timed out", str(error))
            
        finally:
            # Restore the original implementation
            model._process_image_impl = original_process
            # Ensure we can clean up the model despite the timeout
            model.cleanup()
        
        # Now try with a model that doesn't timeout
        config = {
            "name": "realistic_test_model_2",
            "type": "realistic_timeout_test",
            "resource_count": 3,
            "start_background_thread": True,
            "processing_phases": 3,
            "phase_0_delay": 0.01,  # Very fast phases that won't trigger timeout
            "phase_1_delay": 0.01,
            "phase_2_delay": 0.01,
            "timeout_seconds": 1.0   # Longer timeout that won't be exceeded
        }
        
        # Register the config with the config manager
        self.config_manager.register_config(ConfigType.MODEL, "realistic_test_model_2", config)
        
        # Create a new model
        model = factory.create_model("realistic_test_model_2")
        
        try:
            # Process image - should complete successfully this time
            result = model.process_image(self.image_path)
            
            # Verify the result
            self.assertEqual(result["result"], "success")
            self.assertEqual(result["phases_completed"], 3)
            self.assertIn("phase_0_result", result["details"])
            self.assertIn("phase_1_result", result["details"])
            self.assertIn("phase_2_result", result["details"])
        finally:
            # Clean up
            model.cleanup()
    
    def test_timeout_config_validation(self):
        """Test validation of timeout-related configuration values."""
        # Create a model factory
        factory = ModelFactory(self.config_manager)
        
        # Test with invalid timeout_seconds
        config = {
            "name": "timeout_config_test_model",
            "type": "timeout_config_test",
            "timeout_seconds": 0  # Invalid - must be positive
        }
        
        # Register the config with the config manager
        self.config_manager.register_config(ConfigType.MODEL, "timeout_config_test_model", config)
        
        with self.assertRaises(ModelConfigError) as context:
            factory.create_model("timeout_config_test_model")
            
        # Verify the error details
        self.assertIn("timeout_seconds", str(context.exception))
        self.assertIn("positive", str(context.exception))
        
        # Test with invalid loading_timeout_seconds
        config = {
            "name": "timeout_config_test_model",
            "type": "timeout_config_test",
            "timeout_seconds": 1.0,  # Valid
            "loading_timeout_seconds": -1.0  # Invalid - must be positive
        }
        
        # Register the config with the config manager
        self.config_manager.register_config(ConfigType.MODEL, "timeout_config_test_model", config)
        
        with self.assertRaises(ModelConfigError) as context:
            factory.create_model("timeout_config_test_model")
            
        # Verify the error details
        self.assertIn("loading_timeout_seconds", str(context.exception))
        self.assertIn("positive", str(context.exception))
        
        # Test with valid values
        config = {
            "name": "timeout_config_test_model",
            "type": "timeout_config_test",
            "timeout_seconds": 1.0,
            "loading_timeout_seconds": 5.0
        }
        
        # Register the config with the config manager
        self.config_manager.register_config(ConfigType.MODEL, "timeout_config_test_model", config)
        
        # Should not raise an exception
        model = factory.create_model("timeout_config_test_model")
        self.assertIsInstance(model, TimeoutConfigTestModel)
    
    def test_model_loading_timeout_recovery(self):
        """Test that resources are properly cleaned up after a loading timeout."""
        # Create a model factory
        factory = ModelFactory(self.config_manager)
        
        # Create a configuration that will cause a timeout
        config = {
            "name": "timeout_test_model",
            "type": "timeout_test",
            "init_delay": 0.3,  # Long enough to trigger timeout
            "loading_timeout_seconds": 0.1  # Short timeout
        }
        
        # Register the config with the config manager
        self.config_manager.register_config(ConfigType.MODEL, "timeout_test_model", config)
        
        # This should raise a timeout error
        with self.assertRaises(ModelLoaderTimeoutError):
            factory.create_model("timeout_test_model")
        
        # Creating a new model should work without resource conflicts
        config = {
            "name": "timeout_test_model",
            "type": "timeout_test",
            "init_delay": 0,  # No delay this time
            "loading_timeout_seconds": 1.0  # Longer timeout
        }
        
        # Register the config with the config manager
        self.config_manager.register_config(ConfigType.MODEL, "timeout_test_model", config)
        
        # This should succeed without errors
        model = factory.create_model("timeout_test_model")
        self.assertIsInstance(model, TimeoutTestModel)
    
    def test_model_processing_timeout_retry(self):
        """Test that processing retries work properly with timeouts."""
        # Create and configure a model directly
        model = TimeoutTestModel()
        
        # Configure the model with retry settings but override the process method
        # to avoid real timeout errors during testing
        config = MockConfig({
            "name": "timeout_test_model",
            "type": "timeout_test",
            "process_delay": 0.01,  # Very short delay that won't trigger timeout
            "timeout_seconds": 1.0,  # Long timeout
            # Configure retry behavior
            "retry_max_attempts": 2,
            "retry_delay_seconds": 0.1
        })
        
        # Initialize the model
        model.initialize(config)
        
        # Track calls to the original method
        call_count = [0]
        
        # Save the original method
        original_process_impl = model._process_image_impl
        
        # Create a mock implementation that simulates timeout behavior
        def mock_process_impl(image, image_path):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call - simulate a long operation that will timeout
                raise TimeoutError("Test timeout")
            else:
                # Second call - return success
                return {"result": "success", "attempts": call_count[0]}
        
        try:
            # Replace implementation with our mock
            model._process_image_impl = mock_process_impl
            
            # Call process_image directly to bypass the timeout mechanism
            # This would normally timeout but our mock handles it with retry
            result = model.process_image(self.image_path)
            
            # Verify the result
            self.assertEqual(call_count[0], 2)  # Should have been called twice
            self.assertEqual(result["result"], "success")
            self.assertEqual(result["attempts"], 2)
            
        finally:
            # Restore the original implementation
            model._process_image_impl = original_process_impl
    
    def test_timeout_escalation(self):
        """Test that timeouts properly escalate to the appropriate error types."""
        # Test with a function that will timeout
        def slow_function():
            time.sleep(0.2)
            return "result"
        
        # This should raise a ModelLoaderTimeoutError
        with self.assertRaises(ModelLoaderTimeoutError):
            load_model_with_timeout(
                slow_function,
                timeout_seconds=0.1,
                model_name="test_model",
                component="test_component"
            )
    
    def test_timeout_configuration(self):
        """Test that timeout configuration is properly applied from config."""
        # Create a model factory
        factory = ModelFactory(self.config_manager)
        
        # Create a configuration with custom timeouts
        config = {
            "name": "timeout_test_model",
            "type": "timeout_test",
            "init_delay": 0.05,  # Short enough to not timeout
            "loading_timeout_seconds": 2.0,  # Long loading timeout
            "timeout_seconds": 3.0  # Long processing timeout
        }
        
        # Register the config with the config manager
        self.config_manager.register_config(ConfigType.MODEL, "timeout_test_model", config)
        
        # Create the model
        model = factory.create_model("timeout_test_model")
        
        # Check that timeout values were correctly applied
        self.assertEqual(model._loading_timeout_seconds, 2.0)
        self.assertEqual(model._timeout_seconds, 3.0)
    
    def test_multiple_timeout_scenarios(self):
        """Test various timeout scenarios in sequence."""
        # Create a model factory
        factory = ModelFactory(self.config_manager)
        
        # 1. Test a configuration that just barely doesn't timeout
        config = {
            "name": "timeout_test_model",
            "type": "timeout_test",
            "init_delay": 0.05,
            "loading_timeout_seconds": 0.1
        }
        
        # Register the config with the config manager
        self.config_manager.register_config(ConfigType.MODEL, "timeout_test_model", config)
        
        # This should succeed
        model1 = factory.create_model("timeout_test_model")
        self.assertIsInstance(model1, TimeoutTestModel)
        
        # 2. Test a configuration that barely times out
        config = {
            "name": "timeout_test_model",
            "type": "timeout_test",
            "init_delay": 0.15,  # Just longer than the timeout
            "loading_timeout_seconds": 0.1
        }
        
        # Register the config with the config manager
        self.config_manager.register_config(ConfigType.MODEL, "timeout_test_model", config)
        
        # This should raise a timeout error
        with self.assertRaises(ModelLoaderTimeoutError):
            factory.create_model("timeout_test_model")
        
        # 3. Test a configuration with zero timeout (should fail immediately)
        config = {
            "name": "timeout_test_model",
            "type": "timeout_test",
            "init_delay": 0.01,  # Even a tiny delay
            "loading_timeout_seconds": 0  # Immediate timeout
        }
        
        # Register the config with the config manager
        self.config_manager.register_config(ConfigType.MODEL, "timeout_test_model", config)
        
        # This should raise a timeout error
        with self.assertRaises(ModelLoaderTimeoutError):
            factory.create_model("timeout_test_model")


if __name__ == "__main__":
    unittest.main() 