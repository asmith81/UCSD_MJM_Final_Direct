"""
Tests for the PromptFactory implementation.
"""
import pytest
from unittest.mock import Mock, patch

from src.prompts.prompt_factory import PromptFactory
from src.prompts.base_prompt_generator import BasePromptGenerator
from src.config import ConfigType

# Mock prompt generator for testing
class MockPromptGenerator(BasePromptGenerator):
    """Mock prompt generator for testing."""
    
    def __init__(self, config, field):
        self.config = config
        self.field = field
        
    def generate_prompt(self, data):
        return f"Mock prompt for {self.field}: {data}"

class TestPromptFactory:
    """Tests for PromptFactory implementation."""
    
    @pytest.fixture
    def mock_config_manager(self):
        """Create a mock config manager."""
        mock = Mock()
        mock_config = Mock()
        
        # Set up mock config to return sample prompts
        mock_config.get_prompts_by_field.side_effect = lambda field: [
            {"category": "basic", "template": "Test template"}
        ]
        
        mock.get_config.return_value = mock_config
        return mock
        
    @pytest.fixture
    def factory(self, mock_config_manager):
        """Create a PromptFactory instance for testing."""
        # Clear registry before each test
        original_registry = PromptFactory.PROMPT_REGISTRY.copy()
        # Register our mock generator
        PromptFactory.PROMPT_REGISTRY = {"basic": MockPromptGenerator}
        
        factory = PromptFactory(mock_config_manager)
        
        yield factory
        
        # Restore registry
        PromptFactory.PROMPT_REGISTRY = original_registry
    
    def test_factory_initialization(self, mock_config_manager):
        """Test factory initialization."""
        factory = PromptFactory(mock_config_manager)
        assert factory._config_manager == mock_config_manager
    
    def test_factory_initialization_fails_without_config(self):
        """Test that factory requires a config manager."""
        with pytest.raises(ValueError, match="config_manager is required"):
            PromptFactory(None)
    
    def test_create_prompt_generator(self, factory, mock_config_manager):
        """Test creation of prompt generators."""
        # Set up the mock
        mock_config_manager.get_config.return_value.get_prompts_by_field.return_value = [
            {"category": "basic", "template": "Test template"}
        ]
        
        # Create a prompt generator
        generator = factory.create_prompt_generator("test_prompt", "invoice_number")
        
        # Verify the generator was created with correct parameters
        assert isinstance(generator, MockPromptGenerator)
        assert generator.field == "invoice_number"
        
        # Verify the config manager was called correctly
        mock_config_manager.get_config.assert_called_once_with(ConfigType.PROMPT, "test_prompt")
    
    def test_register_prompt_generator(self):
        """Test registration of prompt generators."""
        # Save original registry
        original_registry = PromptFactory.PROMPT_REGISTRY.copy()
        
        try:
            # Register a new generator
            PromptFactory.register_prompt_generator("mock", MockPromptGenerator)
            
            # Verify it was registered
            assert "mock" in PromptFactory.PROMPT_REGISTRY
            assert PromptFactory.PROMPT_REGISTRY["mock"] == MockPromptGenerator
        finally:
            # Restore original registry
            PromptFactory.PROMPT_REGISTRY = original_registry
    
    def test_create_prompt_generator_no_prompts(self, factory, mock_config_manager):
        """Test error handling when no prompts are found."""
        # Set up the mock to return no prompts
        mock_config_manager.get_config.return_value.get_prompts_by_field.return_value = []
        
        # Attempt to create a generator for a field with no prompts
        with pytest.raises(ValueError, match="No prompts found for field"):
            factory.create_prompt_generator("test_prompt", "unknown_field")
    
    def test_create_prompt_generator_unknown_type(self, factory, mock_config_manager):
        """Test error handling for unknown prompt types."""
        # Set up the mock to return a prompt with unknown type
        mock_config_manager.get_config.return_value.get_prompts_by_field.return_value = [
            {"category": "unknown_type", "template": "Test template"}
        ]
        
        # Attempt to create a generator with unknown type
        with pytest.raises(ValueError, match="Unsupported prompt type"):
            factory.create_prompt_generator("test_prompt", "invoice_number") 