"""
Simple test for direct validation of PromptFactory error cases.
"""
import pytest
from unittest.mock import Mock

from src.prompts.prompt_factory import PromptFactory
from src.config import ConfigType


def test_direct_no_prompts():
    """Test that PromptFactory raises ValueError when no prompts are found."""
    # Create mock config manager
    mock_config_manager = Mock()
    mock_config = Mock()
    mock_config_manager.get_config.return_value = mock_config
    
    # Set up mock to return empty prompt list
    mock_config.get_prompts_by_field.return_value = []
    
    factory = PromptFactory(mock_config_manager)
    
    # This should raise a ValueError
    with pytest.raises(ValueError, match="No prompts found for field"):
        factory.create_prompt_generator("test_prompt", "unknown_field")


def test_direct_unknown_type():
    """Test that PromptFactory raises ValueError for unknown prompt types."""
    # Create mock config manager
    mock_config_manager = Mock()
    mock_config = Mock()
    mock_config_manager.get_config.return_value = mock_config
    
    # Set up mock to return a prompt with unknown type
    mock_config.get_prompts_by_field.return_value = [
        {"category": "unknown_type", "template": "Test template"}
    ]
    
    factory = PromptFactory(mock_config_manager)
    
    # This should raise a ValueError
    with pytest.raises(ValueError, match="Unsupported prompt type"):
        factory.create_prompt_generator("test_prompt", "invoice_number") 