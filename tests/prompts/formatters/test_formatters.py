"""Test cases for prompt formatters.

This module contains test cases for each prompt formatter implementation,
using verified examples from model documentation.
"""

import pytest
from pathlib import Path
from typing import Dict, Any

from src.config.base_config import BaseConfig
from src.prompts.formatters.base_prompt_formatter import (
    ModelFormatError,
    FormatValidationError
)
from src.prompts.formatters.implementations.basic_formatter import BasicFormatter
from src.prompts.formatters.implementations.llama_formatter import LlamaFormatter
from src.prompts.formatters.implementations.pixtral_formatter import PixtralFormatter
from src.prompts.formatters.implementations.doctr_formatter import DoctrFormatter


class MockConfig(BaseConfig):
    """Mock configuration for testing."""
    
    def __init__(self, data: Dict[str, Any]):
        self._data = data
        
    def get_data(self) -> Dict[str, Any]:
        return self._data


@pytest.fixture
def basic_config() -> BaseConfig:
    """Create basic formatter configuration."""
    return MockConfig({
        "formats": {
            "basic": {
                "validation": {
                    "required_sections": ["prompt"],
                    "max_tokens": 1024
                },
                "max_length": 2048,
                "format_template": "{prompt}"
            }
        }
    })


@pytest.fixture
def pixtral_config() -> BaseConfig:
    """Create Pixtral formatter configuration."""
    return MockConfig({
        "formats": {
            "pixtral": {
                "validation": {
                    "required_sections": ["system", "prompt"],
                    "max_tokens": 2048
                },
                "max_length": 4096,
                "format_template": "{system}\n\nUser: {prompt}\nAssistant:",
                "system_message": "You are a helpful assistant."
            }
        }
    })


@pytest.fixture
def llama_config() -> BaseConfig:
    """Create Llama formatter configuration."""
    return MockConfig({
        "formats": {
            "llama": {
                "validation": {
                    "required_sections": ["system", "prompt"],
                    "max_tokens": 2048
                },
                "max_length": 4096,
                "format_template": "<s>[INST] <<SYS>>\n{system}\n<</SYS>>\n\n{prompt}[/INST]",
                "system_message": "You are a helpful assistant."
            }
        }
    })


@pytest.fixture
def doctr_config() -> BaseConfig:
    """Create Doctr formatter configuration."""
    return MockConfig({
        "formats": {
            "doctr": {
                "validation": {
                    "required_sections": ["prompt"],
                    "max_tokens": 1024
                },
                "max_length": 2048,
                "format_template": "{prompt}"
            }
        }
    })


def test_basic_formatter(basic_config: BaseConfig):
    """Test basic formatter with verified examples."""
    formatter = BasicFormatter()
    formatter.initialize(basic_config)
    
    # Test simple prompt
    prompt = "Extract the total amount."
    formatted = formatter.format_prompt(prompt, "basic")
    assert formatted == prompt
    
    # Test validation
    assert formatter.validate_format(formatted, "basic")
    
    # Test length validation
    long_prompt = "x" * 3000
    with pytest.raises(FormatValidationError):
        formatter.format_prompt(long_prompt, "basic")


def test_pixtral_formatter(pixtral_config: BaseConfig):
    """Test Pixtral formatter with verified examples."""
    formatter = PixtralFormatter()
    formatter.initialize(pixtral_config)
    
    # Test with system message
    prompt = "Extract the total amount."
    formatted = formatter.format_prompt(prompt, "pixtral")
    expected = "You are a helpful assistant.\n\nUser: Extract the total amount.\nAssistant:"
    assert formatted == expected
    
    # Test validation
    assert formatter.validate_format(formatted, "pixtral")
    
    # Test missing system message
    with pytest.raises(FormatValidationError):
        formatter.validate_format("User: test", "pixtral")


def test_llama_formatter(llama_config: BaseConfig):
    """Test Llama formatter with verified examples."""
    formatter = LlamaFormatter()
    formatter.initialize(llama_config)
    
    # Test with system message
    prompt = "Extract the total amount."
    formatted = formatter.format_prompt(prompt, "llama")
    expected = "<s>[INST] <<SYS>>\nYou are a helpful assistant.\n<</SYS>>\n\nExtract the total amount.[/INST]"
    assert formatted == expected
    
    # Test validation
    assert formatter.validate_format(formatted, "llama")
    
    # Test missing tokens
    with pytest.raises(FormatValidationError):
        formatter.validate_format("Extract the total amount.", "llama")
    
    # Test missing system section
    with pytest.raises(FormatValidationError):
        formatter.validate_format("<s>[INST] Extract amount [/INST]", "llama")


def test_doctr_formatter(doctr_config: BaseConfig):
    """Test Doctr formatter with verified examples."""
    formatter = DoctrFormatter()
    formatter.initialize(doctr_config)
    
    # Test simple prompt
    prompt = "Extract the total amount."
    formatted = formatter.format_prompt(prompt, "doctr")
    assert formatted == prompt
    
    # Test validation
    assert formatter.validate_format(formatted, "doctr")
    
    # Test length validation
    long_prompt = "x" * 3000
    with pytest.raises(FormatValidationError):
        formatter.format_prompt(long_prompt, "doctr") 