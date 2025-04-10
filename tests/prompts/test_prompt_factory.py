"""Tests for the PromptFactory class."""
import pytest
from pathlib import Path
from decimal import Decimal
from typing import Dict, Any

from src.prompts.prompt_factory import (
    PromptFactory,
    PromptFactoryError,
    PromptConfigError,
    PromptGeneratorError
)
from src.prompts.base_prompt_generator import BasePromptGenerator
from src.prompts.prompt_config import PromptConfig
from src.config.base_config import BaseConfig


class MockPromptGenerator(BasePromptGenerator):
    """Mock prompt generator for testing."""
    def __init__(self):
        self.initialized = False
        self.cleaned_up = False
        self.config = None
        
    def initialize(self, config: BaseConfig) -> None:
        self.initialized = True
        self.config = config
        
    def generate_prompt(self, context: Dict[str, Any]) -> str:
        return "mock prompt"
        
    def validate_config(self, config: BaseConfig) -> bool:
        # Actually validate the config for testing
        if not isinstance(config, PromptConfig):
            return False
        for prompt in config.prompts:
            if not all([prompt.name, prompt.text, prompt.category]):
                return False
            if prompt.metadata and 'examples' in prompt.metadata:
                for example in prompt.metadata['examples']:
                    if 'output' not in example:
                        return False
        return True
        
    def get_template(self, template_name: str) -> Any:
        return None
        
    def get_templates_for_field(self, field_type: str) -> list:
        return []
        
    def cleanup(self) -> None:
        self.cleaned_up = True


@pytest.fixture(autouse=True)
def clear_registry():
    """Clear the PromptFactory registry before each test."""
    # Add 'test' to valid categories for testing
    PromptFactory.VALID_CATEGORIES.add('test')
    # Clear registry and prevent default registration
    PromptFactory.REGISTRY.clear()
    # Clear active generators
    PromptFactory._active_generators.clear()
    # Disable default registration by monkeypatching
    original_register = PromptFactory._register_default_generators
    PromptFactory._register_default_generators = lambda self: None
    yield
    # Restore original method and cleanup
    PromptFactory._register_default_generators = original_register
    PromptFactory.VALID_CATEGORIES.remove('test')
    PromptFactory.REGISTRY.clear()
    PromptFactory._active_generators.clear()


@pytest.fixture
def config_dir(tmp_path) -> Path:
    """Create a temporary config directory with test YAML files."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    # Create basic.yaml
    basic_yaml = {
        "config_info": {
            "name": "Basic Prompts",
            "version": "1.0"
        },
        "prompts": [
            {
                "name": "work_order_basic",
                "text": "Extract the work order number",
                "category": "basic",
                "field_to_extract": "work_order",
                "format_instructions": "5 alphanumeric characters"
            },
            {
                "name": "cost_basic",
                "text": "Extract the total cost",
                "category": "basic",
                "field_to_extract": "cost",
                "format_instructions": "Positive number with up to 2 decimal places",
                "metadata": {
                    "examples": [
                        {"input": "Total: $123.45", "output": "123.45"},
                        {"input": "Amount: $50.00", "output": "50.00"}
                    ]
                }
            }
        ]
    }
    
    with open(config_dir / "basic.yaml", 'w') as f:
        import yaml
        yaml.dump(basic_yaml, f)
    
    return config_dir


@pytest.fixture
def factory(config_dir) -> PromptFactory:
    """Create a PromptFactory instance with test configuration."""
    return PromptFactory(config_dir)


def test_factory_initialization(config_dir):
    """Test factory initialization."""
    # Test successful initialization
    factory = PromptFactory(config_dir)
    assert isinstance(factory, PromptFactory)
    
    # Test initialization without config_dir
    with pytest.raises(ValueError):
        PromptFactory(None)


def test_register_generator(factory):
    """Test generator registration."""
    # Test successful registration
    factory.register_generator('test', MockPromptGenerator)
    assert 'test' in factory.REGISTRY
    assert factory.REGISTRY['test'] == MockPromptGenerator
    
    # Test invalid category
    with pytest.raises(ValueError):
        factory.register_generator('invalid', MockPromptGenerator)
    
    # Test invalid generator class
    class InvalidGenerator:
        pass
    
    with pytest.raises(TypeError):
        factory.register_generator('basic', InvalidGenerator)
    
    # Test duplicate registration
    with pytest.raises(ValueError):
        factory.register_generator('test', MockPromptGenerator)


def test_create_generator(factory):
    """Test generator creation."""
    # Register mock generator
    factory.register_generator('basic', MockPromptGenerator)
    
    # Test successful creation
    generator = factory.create_generator('basic', 'work_order')
    assert isinstance(generator, MockPromptGenerator)
    assert generator.initialized
    
    # Test invalid category
    with pytest.raises(ValueError):
        factory.create_generator('invalid', 'work_order')
    
    # Test invalid field type
    with pytest.raises(ValueError):
        factory.create_generator('basic', 'invalid')
    
    # Test unregistered category
    with pytest.raises(PromptFactoryError):
        factory.create_generator('detailed', 'work_order')


def test_validate_config(factory):
    """Test configuration validation."""
    # Register mock generator
    factory.register_generator('basic', MockPromptGenerator)
    
    # Test valid work order config
    config = PromptConfig(prompts=[{
        "name": "test",
        "text": "test",
        "category": "basic",
        "field_to_extract": "work_order",
        "format_instructions": "5 alphanumeric characters"
    }])
    
    assert factory._validate_config(config, 'basic', 'work_order')
    
    # Test valid cost config with examples
    config = PromptConfig(prompts=[{
        "name": "test",
        "text": "test",
        "category": "basic",
        "field_to_extract": "cost",
        "format_instructions": "Positive number with up to 2 decimal places",
        "metadata": {
            "examples": [
                {"output": "123.45"},
                {"output": "50.00"}
            ]
        }
    }])
    
    assert factory._validate_config(config, 'basic', 'cost')
    
    # Test invalid work order example
    config = PromptConfig(prompts=[{
        "name": "test",
        "text": "test",
        "category": "basic",
        "field_to_extract": "work_order",
        "metadata": {
            "examples": [
                {"output": "123"}  # Invalid: not 5 alphanumeric characters
            ]
        }
    }])
    
    with pytest.raises(PromptConfigError):
        factory._validate_config(config, 'basic', 'work_order')


def test_cleanup(factory):
    """Test cleanup of active generators."""
    # Register and create multiple generators
    factory.register_generator('basic', MockPromptGenerator)
    gen1 = factory.create_generator('basic', 'work_order')
    gen2 = factory.create_generator('basic', 'cost')
    
    # Verify generators are tracked
    assert len(factory._active_generators) == 2
    
    # Test cleanup
    factory.cleanup()
    
    # Verify all generators were cleaned up
    assert len(factory._active_generators) == 0
    assert gen1.cleaned_up
    assert gen2.cleaned_up


def test_load_config(factory, config_dir):
    """Test configuration loading."""
    # Test successful load
    config = factory._load_config('basic', 'work_order')
    assert isinstance(config, PromptConfig)
    assert len(config.prompts) == 1
    assert config.prompts[0].name == 'work_order_basic'
    
    # Test missing file
    with pytest.raises(PromptFactoryError):
        factory._load_config('missing', 'work_order')
    
    # Test missing field type
    with pytest.raises(PromptFactoryError):
        factory._load_config('basic', 'missing') 