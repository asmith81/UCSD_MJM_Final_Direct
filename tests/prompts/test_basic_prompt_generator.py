"""Tests for the BasicPromptGenerator implementation."""

import pytest
from typing import Dict, Any

from src.prompts.implementations.basic_prompt_generator import BasicPromptGenerator
from src.prompts.prompt_config import PromptConfig, PromptTemplate


@pytest.fixture
def basic_config() -> PromptConfig:
    """Create a basic test configuration."""
    prompts = [
        {
            "name": "work_order_basic",
            "text": "Find the work order number in the image.",
            "category": "basic",
            "field_to_extract": "work_order",
            "description": "Basic work order prompt"
        },
        {
            "name": "cost_basic",
            "text": "Find the total cost in the image.",
            "category": "basic",
            "field_to_extract": "cost",
            "description": "Basic cost prompt"
        }
    ]
    return PromptConfig(prompts=prompts)


@pytest.fixture
def generator() -> BasicPromptGenerator:
    """Create a BasicPromptGenerator instance."""
    return BasicPromptGenerator()


def test_initialization(generator: BasicPromptGenerator, basic_config: PromptConfig):
    """Test generator initialization."""
    generator.initialize(basic_config)
    
    # Verify templates were cached
    work_order_template = generator.get_template("work_order_basic")
    assert work_order_template is not None
    assert work_order_template.name == "work_order_basic"
    
    cost_template = generator.get_template("cost_basic")
    assert cost_template is not None
    assert cost_template.name == "cost_basic"


def test_validate_config(generator: BasicPromptGenerator, basic_config: PromptConfig):
    """Test configuration validation."""
    # Valid config should pass
    assert generator.validate_config(basic_config) is True
    
    # Test invalid configs
    with pytest.raises(ValueError, match="Config must be instance of PromptConfig"):
        generator.validate_config({})  # type: ignore
        
    empty_config = PromptConfig(prompts=[])
    with pytest.raises(ValueError, match="Configuration must include at least one prompt"):
        generator.validate_config(empty_config)
        
    invalid_prompt = PromptConfig(prompts=[{
        "name": "",
        "text": "",
        "category": "basic",
        "field_to_extract": "work_order"
    }])
    with pytest.raises(ValueError, match="Prompts must have name and text"):
        generator.validate_config(invalid_prompt)


def test_generate_prompt(generator: BasicPromptGenerator, basic_config: PromptConfig):
    """Test prompt generation."""
    generator.initialize(basic_config)
    
    # Test basic work order prompt
    context = {"field_type": "work_order"}
    prompt = generator.generate_prompt(context)
    assert "Find the work order number" in prompt
    assert "exactly 5 alphanumeric characters" in prompt
    
    # Test basic cost prompt
    context = {"field_type": "cost"}
    prompt = generator.generate_prompt(context)
    assert "Find the total cost" in prompt
    assert "decimal number with exactly 2 decimal places" in prompt
    
    # Test with custom format instructions
    context = {
        "field_type": "work_order",
        "format_instructions": "Custom instructions"
    }
    prompt = generator.generate_prompt(context)
    assert "Custom instructions" in prompt
    
    # Test with examples
    context = {
        "field_type": "work_order",
        "examples": ["Example 1", "Example 2"]
    }
    prompt = generator.generate_prompt(context)
    assert "Examples:" in prompt
    assert "Example 1" in prompt
    assert "Example 2" in prompt


def test_get_template(generator: BasicPromptGenerator, basic_config: PromptConfig):
    """Test template retrieval by name."""
    generator.initialize(basic_config)
    
    # Test existing template
    template = generator.get_template("work_order_basic")
    assert template is not None
    assert template.name == "work_order_basic"
    assert template.field_to_extract == "work_order"
    
    # Test non-existent template
    template = generator.get_template("non_existent")
    assert template is None


def test_get_templates_for_field(generator: BasicPromptGenerator, basic_config: PromptConfig):
    """Test template retrieval by field type."""
    generator.initialize(basic_config)
    
    # Test existing field
    templates = generator.get_templates_for_field("work_order")
    assert len(templates) == 1
    assert templates[0].name == "work_order_basic"
    
    # Test non-existent field
    templates = generator.get_templates_for_field("non_existent")
    assert len(templates) == 0


def test_cleanup(generator: BasicPromptGenerator, basic_config: PromptConfig):
    """Test resource cleanup."""
    generator.initialize(basic_config)
    
    # Verify initialized state
    assert generator._config is not None
    assert len(generator._templates) > 0
    
    # Cleanup
    generator.cleanup()
    
    # Verify cleaned state
    assert generator._config is None
    assert len(generator._templates) == 0
    assert generator._current_prompt is None


def test_error_handling(generator: BasicPromptGenerator, basic_config: PromptConfig):
    """Test error handling scenarios."""
    # Test uninitialized generator
    with pytest.raises(RuntimeError, match="Generator not initialized"):
        generator.generate_prompt({"field_type": "work_order"})
        
    generator.initialize(basic_config)
    
    # Test missing field_type
    with pytest.raises(ValueError, match="Context must include field_type"):
        generator.generate_prompt({})
        
    # Test invalid field_type
    with pytest.raises(ValueError, match="No prompts found for field type"):
        generator.generate_prompt({"field_type": "invalid"}) 