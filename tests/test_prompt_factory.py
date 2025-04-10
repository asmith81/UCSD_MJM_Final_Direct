"""
Tests for the PromptFactory implementation.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.prompts.prompt_factory import PromptFactory, PromptFactoryError
from src.prompts.base_prompt_generator import BasePromptGenerator
from src.prompts.prompt_config import PromptConfig
from src.prompts.implementations.basic_prompt_generator import BasicPromptGenerator

# Mock prompt generator for testing
class MockPromptGenerator(BasePromptGenerator):
    """Mock prompt generator for testing."""
    
    def initialize(self, config):
        self.config = config
        
    def generate_prompt(self, context):
        return "mock prompt"

@pytest.fixture
def config_dir(tmp_path):
    """Create a temporary config directory with test files."""
    config_dir = tmp_path / "config" / "prompts"
    config_dir.mkdir(parents=True)
    
    # Create basic.yaml
    basic_yaml = """
config_info:
  name: basic_prompts
  version: "1.0"
prompts:
  - name: basic_work_order
    text: "Extract the work order number."
    category: basic
    field_to_extract: work_order
    description: "Basic work order prompt"
    version: "1.0"
    format_instructions: {}
    metadata: {}
  - name: basic_cost
    text: "Extract the total cost."
    category: basic
    field_to_extract: cost
    description: "Basic cost prompt"
    version: "1.0"
    format_instructions: {}
    metadata: {}
"""
    (config_dir / "basic.yaml").write_text(basic_yaml)
    
    return config_dir

@pytest.fixture
def factory(config_dir):
    """Create a PromptFactory instance for testing."""
    return PromptFactory(config_dir)

def test_register_generator():
    """Test registering a new generator."""
    PromptFactory.REGISTRY.clear()  # Start fresh
    
    # Register valid generator
    PromptFactory.register_generator("basic", MockPromptGenerator)
    assert "basic" in PromptFactory.REGISTRY
    assert PromptFactory.REGISTRY["basic"] == MockPromptGenerator
    
    # Try registering invalid category
    with pytest.raises(ValueError):
        PromptFactory.register_generator("invalid", MockPromptGenerator)
        
    # Try registering invalid class
    class NotAGenerator:
        pass
        
    with pytest.raises(TypeError):
        PromptFactory.register_generator("basic", NotAGenerator)
        
    # Try registering duplicate
    with pytest.raises(ValueError):
        PromptFactory.register_generator("basic", MockPromptGenerator)

def test_create_generator(factory):
    """Test creating a generator instance."""
    # Register a test generator
    PromptFactory.REGISTRY.clear()
    PromptFactory.register_generator("basic", MockPromptGenerator)
    
    # Create with valid inputs
    generator = factory.create_generator("basic", "work_order")
    assert isinstance(generator, MockPromptGenerator)
    
    # Try invalid category
    with pytest.raises(ValueError):
        factory.create_generator("invalid", "work_order")
        
    # Try invalid field type
    with pytest.raises(ValueError):
        factory.create_generator("basic", "invalid")
        
    # Try unregistered category
    PromptFactory.REGISTRY.clear()
    with pytest.raises(PromptFactoryError):
        factory.create_generator("basic", "work_order")

def test_load_config(factory):
    """Test loading configuration from files."""
    # Load valid config
    config = factory._load_config("basic", "work_order")
    assert isinstance(config, PromptConfig)
    assert len(config.get_prompts_for_field("work_order")) == 1
    
    # Try loading non-existent file
    with pytest.raises(PromptFactoryError):
        factory._load_config("nonexistent", "work_order")
        
    # Try loading for non-existent field type
    with pytest.raises(PromptFactoryError):
        factory._load_config("basic", "invalid")

def test_basic_generator_integration(factory):
    """Test integration with BasicPromptGenerator."""
    # Register the actual BasicPromptGenerator
    PromptFactory.REGISTRY.clear()
    PromptFactory.register_generator("basic", BasicPromptGenerator)
    
    # Create generator
    generator = factory.create_generator("basic", "work_order")
    assert isinstance(generator, BasicPromptGenerator)
    
    # Generate a prompt
    prompt = generator.generate_prompt({"field_type": "work_order"})
    assert "work order number" in prompt.lower()
    assert "5 alphanumeric characters" in prompt
    
    # Test with cost field
    generator = factory.create_generator("basic", "cost")
    prompt = generator.generate_prompt({"field_type": "cost"})
    assert "total" in prompt.lower()
    assert "decimal" in prompt 