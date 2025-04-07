"""
Tests for the ModelFactory implementation.
"""
import pytest
from unittest.mock import Mock, patch

from src.models.model_factory import ModelFactory, ModelCreationError
from src.models.base_model import BaseModel, ModelInitializationError
from src.config.base_config import BaseConfig
from src.config import ConfigType
from src.config.implementations.model_config import ModelConfig
from src.config.config_manager import ConfigManager

class MockModel(BaseModel):
    """Mock model implementation for testing."""
    def initialize(self, config):
        pass
    
    def process_image(self, image_path):
        return {}
    
    def validate_config(self, config):
        return True

class FailingModel(BaseModel):
    """Mock model that fails initialization."""
    def initialize(self, config):
        raise ModelInitializationError("Failed to initialize")
    
    def process_image(self, image_path):
        return {}
    
    def validate_config(self, config):
        return False

@pytest.fixture
def mock_config_manager():
    """Create a mock config manager."""
    mock = Mock()
    return mock

@pytest.fixture
def factory(mock_config_manager):
    """Create a ModelFactory instance for testing."""
    # Clear registry before each test
    ModelFactory.MODEL_REGISTRY.clear()
    return ModelFactory(config_manager=mock_config_manager)

@pytest.fixture
def mock_config():
    """Create a mock ModelConfig for testing."""
    config = Mock(spec=ModelConfig)
    config.get_value.return_value = "mock"
    return config

def test_model_factory_initialization(mock_config_manager):
    """Test ModelFactory initialization."""
    # Test with custom config manager
    factory = ModelFactory(config_manager=mock_config_manager)
    assert factory._config_manager == mock_config_manager

    # Test with default config manager
    with patch("src.models.model_factory.get_config_manager") as mock_get_config:
        mock_get_config.return_value = mock_config_manager
        factory = ModelFactory()
        assert factory._config_manager == mock_config_manager

def test_register_model(factory):
    """Test model registration."""
    # Test valid registration
    ModelFactory.register_model("mock", MockModel)
    assert "mock" in ModelFactory.MODEL_REGISTRY
    assert ModelFactory.MODEL_REGISTRY["mock"] == MockModel

    # Test invalid model type
    with pytest.raises(ValueError, match="Model type must be a non-empty string"):
        ModelFactory.register_model("", MockModel)
    with pytest.raises(ValueError, match="Model type must be a non-empty string"):
        ModelFactory.register_model(None, MockModel)

    # Test invalid model class
    class InvalidModel:
        pass
    
    with pytest.raises(ValueError, match="Model class must implement BaseModel interface"):
        ModelFactory.register_model("invalid", InvalidModel)

def test_create_model_success(factory, mock_config):
    """Test successful model creation."""
    # Register mock model
    ModelFactory.register_model("mock", MockModel)
    
    # Test with explicit config
    model = factory.create_model("test_model", mock_config)
    assert isinstance(model, MockModel)
    
    # Test with loaded config
    factory._config_manager.get_config.return_value = mock_config
    model = factory.create_model("test_model")
    assert isinstance(model, MockModel)

def test_create_model_failures(factory, mock_config):
    """Test model creation failures."""
    # Register failing model
    ModelFactory.register_model("failing", FailingModel)
    mock_config.get_value.return_value = "failing"
    
    # Test initialization failure
    with pytest.raises(ModelCreationError, match="Failed to create model test_model"):
        factory.create_model("test_model", mock_config)
    
    # Test invalid model type
    mock_config.get_value.return_value = "invalid_type"
    with pytest.raises(ModelCreationError, match="Unsupported model type"):
        factory.create_model("test_model", mock_config)
    
    # Test config validation failure
    mock_config.get_value.return_value = "failing"
    with pytest.raises(ModelCreationError, match="Invalid configuration"):
        factory.create_model("test_model", mock_config)

def test_load_model_config(factory):
    """Test model configuration loading."""
    # Test valid config loading
    mock_config = Mock(spec=ModelConfig)
    factory._config_manager.get_config.return_value = mock_config
    config = factory._load_model_config("test_model")
    assert config == mock_config
    
    # Test invalid config type
    invalid_config = Mock(spec=BaseConfig)  # Not a ModelConfig
    factory._config_manager.get_config.return_value = invalid_config
    with pytest.raises(ValueError, match="Invalid configuration type"):
        factory._load_model_config("test_model")

def test_model_factory_integration(factory, mock_config):
    """Test ModelFactory integration with config and models."""
    # Register test models
    ModelFactory.register_model("mock", MockModel)
    ModelFactory.register_model("failing", FailingModel)
    
    # Test successful flow
    mock_config.get_value.return_value = "mock"
    factory._config_manager.get_config.return_value = mock_config
    
    model = factory.create_model("test_model")
    assert isinstance(model, MockModel)
    
    # Test failure flow
    mock_config.get_value.return_value = "failing"
    with pytest.raises(ModelCreationError):
        factory.create_model("test_model")

def test_factory_init_without_config_manager():
    """Test factory initialization without config manager."""
    # Should raise ValueError when config_manager is None
    with pytest.raises(ValueError, match="config_manager is required"):
        ModelFactory(None) 