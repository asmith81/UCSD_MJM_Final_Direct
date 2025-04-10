"""
Test the model factory.

This module tests the model factory to ensure proper model
registration, initialization, and error handling.
"""
import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Any

from src.models.model_factory import ModelFactory
from src.models.base_model import BaseModel
from src.models.model_errors import (
    ModelCreationError, 
    ModelConfigError,
    ModelInitializationError,
    ModelResourceError
)
from src.config.base_config import BaseConfig
from src.config.base_config_manager import BaseConfigManager
from src.config.implementations.model_config import ModelConfig


# Mock configuration class for testing
class MockConfig(BaseConfig):
    def __init__(self, data: Dict[str, Any]):
        self._data = data
        
    def get_data(self) -> Dict[str, Any]:
        return self._data
    
    def get_value(self, key: str, default=None):
        return self._data.get(key, default)
        
    def has_value(self, key: str) -> bool:
        return key in self._data
        
    def validate(self) -> bool:
        """
        Validate the configuration data.
        
        Returns:
            bool: True if configuration is valid
        """
        return True
        
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire section of the configuration.
        
        Args:
            section: The section name
            
        Returns:
            Dict[str, Any]: The section data or an empty dict if not found
        """
        return self._data.get(section, {})


# Mock model implementation for testing
class MockModel(BaseModel):
    def __init__(self):
        self.initialized = False
        self.config = None
        
    def initialize(self, config: BaseConfig) -> None:
        self.initialized = True
        self.config = config
        
    def process_image(self, image_path):
        if not self.initialized:
            raise ValueError("Not initialized")
        return {"result": "mock_result"}
        
    def validate_config(self, config: BaseConfig) -> bool:
        return True


# Mock model with validation failure
class MockInvalidModel(BaseModel):
    def initialize(self, config: BaseConfig) -> None:
        pass
        
    def process_image(self, image_path):
        return {}
        
    def validate_config(self, config: BaseConfig) -> bool:
        return False


# Mock model with initialization error
class MockErrorModel(BaseModel):
    def initialize(self, config: BaseConfig) -> None:
        raise ModelInitializationError("Initialization failed")
        
    def process_image(self, image_path):
        return {}
        
    def validate_config(self, config: BaseConfig) -> bool:
        return True


# Mock model with resource error
class MockResourceErrorModel(BaseModel):
    def initialize(self, config: BaseConfig) -> None:
        raise ModelResourceError("Resource not available")
        
    def process_image(self, image_path):
        return {}
        
    def validate_config(self, config: BaseConfig) -> bool:
        return True


class TestModelFactory:
    """Test the ModelFactory class and its error handling."""
    
    @pytest.fixture
    def config_manager(self):
        """Create a mock configuration manager."""
        manager = MagicMock()
        mock_config = MagicMock(spec=ModelConfig)
        # Set up necessary methods that will be called
        mock_config.get_value.side_effect = lambda key, default=None: {
            "name": "test_model",
            "type": "mock_model",
            "version": "1.0"
        }.get(key, default)
        mock_config.validate.return_value = True
        manager.get_config.return_value = mock_config
        return manager
    
    @pytest.fixture
    def clean_registry(self):
        """Clear and restore model registry between tests."""
        original_registry = ModelFactory.MODEL_REGISTRY.copy()
        ModelFactory.MODEL_REGISTRY = {}
        yield
        ModelFactory.MODEL_REGISTRY = original_registry
    
    def test_register_model(self, clean_registry):
        """Test model registration."""
        # Register a model
        ModelFactory.register_model("mock_model", MockModel)
        
        # Check registration was successful
        assert "mock_model" in ModelFactory.MODEL_REGISTRY
        assert ModelFactory.MODEL_REGISTRY["mock_model"] == MockModel
        
        # Test invalid registrations
        with pytest.raises(ValueError):
            ModelFactory.register_model("", MockModel)
            
        with pytest.raises(ValueError):
            ModelFactory.register_model("invalid_model", str)  # Not a BaseModel
    
    def test_create_model(self, clean_registry, config_manager):
        """Test model creation and initialization."""
        # Register model
        ModelFactory.register_model("mock_model", MockModel)
        
        # Create factory with mock config manager
        factory = ModelFactory(config_manager)
        
        # Create model
        model = factory.create_model("test_model")
        
        # Verify model was initialized correctly
        assert isinstance(model, MockModel)
        assert model.initialized
        assert model.config.get_value("name") == "test_model"
        assert model.config.get_value("type") == "mock_model"
    
    def test_create_model_with_explicit_config(self, clean_registry):
        """Test model creation with explicit configuration."""
        # Register model
        ModelFactory.register_model("mock_model", MockModel)
        
        # Create factory with mock config manager
        mock_config_manager = MagicMock()
        factory = ModelFactory(mock_config_manager)
        
        # Create explicit config
        config = MockConfig({
            "name": "explicit_model",
            "type": "mock_model",
            "version": "2.0",
            "custom_param": "value"
        })
        
        # Create model with explicit config
        model = factory.create_model("explicit_name", config)
        
        # Verify model was initialized correctly
        assert isinstance(model, MockModel)
        assert model.initialized
        assert model.config.get_value("name") == "explicit_model"
        assert model.config.get_value("custom_param") == "value"
    
    def test_factory_requires_config_manager(self, clean_registry):
        """Test that factory requires config_manager."""
        with pytest.raises(ValueError, match="config_manager is required"):
            ModelFactory(None)
    
    def test_create_model_validation_failure(self, clean_registry, config_manager):
        """Test error handling for validation failure."""
        # Register invalid model
        ModelFactory.register_model("mock_model", MockInvalidModel)
        
        # Create factory
        factory = ModelFactory(config_manager)
        
        # Attempt to create model
        with pytest.raises(ModelConfigError) as excinfo:
            factory.create_model("test_model")
            
        assert "Configuration validation failed" in str(excinfo.value)
    
    def test_create_model_unknown_type(self, clean_registry, config_manager):
        """Test error handling for unknown model type."""
        # Create factory without registering any models
        factory = ModelFactory(config_manager)
        
        # Attempt to create model with unknown type
        with pytest.raises(ModelCreationError) as excinfo:
            factory.create_model("test_model")
            
        assert "Unsupported model type" in str(excinfo.value)
    
    def test_create_model_invalid_config(self, clean_registry, config_manager):
        """Test error handling for invalid configuration."""
        # Register model
        ModelFactory.register_model("mock_model", MockModel)
        
        # Make the config manager return invalid config type
        config_manager.get_config.return_value = "not a config"
        
        # Create factory
        factory = ModelFactory(config_manager)
        
        # Attempt to create model
        with pytest.raises(ModelConfigError) as excinfo:
            factory.create_model("test_model")
            
        assert "Invalid configuration type" in str(excinfo.value)
    
    def test_create_model_missing_type(self, clean_registry, config_manager):
        """Test error handling for missing model type."""
        # Register model
        ModelFactory.register_model("mock_model", MockModel)
        
        # Make the config return None for the type
        mock_config = MagicMock(spec=ModelConfig)
        mock_config.get_value.side_effect = lambda key, default=None: None if key == "type" else "test_value"
        config_manager.get_config.return_value = mock_config
        
        # Create factory
        factory = ModelFactory(config_manager)
        
        # Attempt to create model
        with pytest.raises(ModelConfigError) as excinfo:
            factory.create_model("test_model")
            
        assert "Model type not specified" in str(excinfo.value)
    
    def test_create_model_initialization_error(self, clean_registry, config_manager):
        """Test error handling for initialization error."""
        # Register error model
        ModelFactory.register_model("mock_model", MockErrorModel)
        
        # Create factory
        factory = ModelFactory(config_manager)
        
        # Attempt to create model
        with pytest.raises(ModelInitializationError) as excinfo:
            factory.create_model("test_model")
            
        assert "Initialization failed" in str(excinfo.value)
    
    def test_create_model_resource_error(self, clean_registry, config_manager):
        """Test error handling for resource error."""
        # Register resource error model
        ModelFactory.register_model("mock_model", MockResourceErrorModel)
        
        # Create factory
        factory = ModelFactory(config_manager)
        
        # Attempt to create model
        with pytest.raises(ModelResourceError) as excinfo:
            factory.create_model("test_model")
            
        assert "Resource not available" in str(excinfo.value)
    
    def test_create_model_unexpected_error(self, clean_registry, config_manager):
        """Test error handling for unexpected errors."""
        # Register model class that raises unexpected error
        class BrokenModel(BaseModel):
            def __init__(self):
                raise RuntimeError("Unexpected initialization error")
                
            def initialize(self, config):
                pass
                
            def process_image(self, path):
                return {}
                
            def validate_config(self, config):
                return True
                
        ModelFactory.register_model("mock_model", BrokenModel)
        
        # Create factory
        factory = ModelFactory(config_manager)
        
        # Attempt to create model
        with pytest.raises(ModelCreationError) as excinfo:
            factory.create_model("test_model")
            
        assert "Failed to instantiate model class" in str(excinfo.value)
        assert "Unexpected initialization error" in str(excinfo.value) 