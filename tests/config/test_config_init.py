"""
Tests for configuration system initialization.
"""
import pytest

from src.config import (
    BaseConfig,
    BaseConfigManager,
    ConfigManager,
    ConfigFactory,
    ConfigType,
    ConfigurationError,
)

def test_exports_base_interfaces():
    """Verify base interfaces are exported."""
    assert BaseConfig is not None
    assert BaseConfigManager is not None
    
def test_exports_implementation():
    """Verify concrete implementations are exported."""
    assert ConfigManager is not None
    assert ConfigFactory is not None
    
def test_exports_types_and_errors():
    """Verify types and errors are exported."""
    assert ConfigType is not None
    assert ConfigurationError is not None
    
def test_config_manager_creation():
    """Verify ConfigManager can be created with dependencies."""
    config_factory = ConfigFactory()
    config_manager = ConfigManager(
        config_root="test_configs",
        config_factory=config_factory
    )
    assert isinstance(config_manager, BaseConfigManager)
    
def test_config_manager_validation():
    """Verify ConfigManager validates constructor arguments."""
    with pytest.raises(ValueError):
        ConfigManager(config_root=None, config_factory=ConfigFactory())
        
    with pytest.raises(ValueError):
        ConfigManager(config_root="test", config_factory=None)

def test_config_type_completeness():
    """Verify ConfigType enum has all required configuration types."""
    assert hasattr(ConfigType, 'MODEL')
    assert hasattr(ConfigType, 'PROMPT')
    assert hasattr(ConfigType, 'EVALUATION')
    
def test_config_type_uniqueness():
    """Verify ConfigType values are unique."""
    values = [t.value for t in ConfigType]
    assert len(values) == len(set(values))

def test_config_manager_interface_compliance():
    """Verify ConfigManager implements all required BaseConfigManager methods."""
    required_methods = [
        'get_config',
        'invalidate_cache',
        'reload_config'
    ]
    
    for method in required_methods:
        assert hasattr(ConfigManager, method)
        assert callable(getattr(ConfigManager, method))

def test_config_error_inheritance():
    """Verify ConfigurationError inherits from Exception."""
    assert issubclass(ConfigurationError, Exception)
    
    # Test error instantiation
    error = ConfigurationError("test error")
    assert str(error) == "test error" 