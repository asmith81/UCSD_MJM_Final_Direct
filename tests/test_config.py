import os
import pytest
from pathlib import Path
from src.config.config_manager import ConfigManager, ConfigType, ConfigurationError
from src.config.config_factory import ConfigFactory
from src.config.implementations import ModelConfig, PromptConfig, EvaluationConfig

def get_fixture_path(filename: str) -> str:
    """Helper function to get fixture file paths."""
    return str(Path(__file__).parent / "fixtures" / "config" / filename)

@pytest.fixture
def config_manager():
    """Fixture to create a ConfigManager instance with test fixtures."""
    return ConfigManager(
        config_root=Path(__file__).parent / "fixtures" / "config",
        config_factory=ConfigFactory()
    )

def test_base_config_interface():
    """Test that all config implementations have required methods."""
    for config_class in [ModelConfig, PromptConfig, EvaluationConfig]:
        assert hasattr(config_class, 'validate')
        assert hasattr(config_class, 'get_data')
        assert hasattr(config_class, 'get_value')
        assert hasattr(config_class, 'get_section')

def test_config_loading(config_manager):
    """Test loading configurations of different types."""
    # Test model config loading
    model_config = config_manager.get_config(ConfigType.MODEL, "valid_model")
    assert model_config.get_value("name") == "test_model"
    assert model_config.get_value("type") == "llm"
    assert isinstance(model_config.get_value("parameters"), dict)

    # Test prompt config loading
    prompt_config = config_manager.get_config(ConfigType.PROMPT, "valid_prompt")
    assert prompt_config.get_value("config_info.name") == "detailed_prompts"
    prompts = prompt_config.get_section("prompts")
    assert len(prompts) > 0
    assert all("name" in p for p in prompts)

    # Test evaluation config loading
    eval_config = config_manager.get_config(ConfigType.EVALUATION)
    assert isinstance(eval_config, EvaluationConfig)

def test_config_caching(config_manager):
    """Test that configurations are properly cached."""
    # Load config first time
    config1 = config_manager.get_config(ConfigType.MODEL, "valid_model")
    
    # Load same config again - should return cached instance
    config2 = config_manager.get_config(ConfigType.MODEL, "valid_model")
    assert config1 is config2  # Should be same instance
    
    # Reload config - should be new instance
    config3 = config_manager.reload_config(ConfigType.MODEL, "valid_model")
    assert config1 is not config3  # Should be different instance

def test_config_error_handling(config_manager):
    """Test error handling in configuration loading."""
    # Test nonexistent file
    with pytest.raises(ConfigurationError):
        config_manager.get_config(ConfigType.MODEL, "nonexistent")
    
    # Test invalid YAML
    invalid_path = Path(__file__).parent / "fixtures" / "config" / "prompts" / "invalid_prompt.yaml"
    invalid_path.parent.mkdir(parents=True, exist_ok=True)
    invalid_path.write_text("invalid: yaml: :")
    
    with pytest.raises(ConfigurationError):
        config_manager.get_config(ConfigType.PROMPT, "invalid_prompt")
    
    # Clean up
    invalid_path.unlink()

def test_model_config_validation():
    """Test validation of model config."""
    # Valid config
    valid_config = ModelConfig({
        "model": {
            "name": "test_model",
            "type": "llm",
            "parameters": {}
        }
    })
    assert valid_config.validate() is True

    # Invalid config
    with pytest.raises(ValueError):
        ModelConfig({}).validate()

def test_prompt_config_validation():
    """Test validation of prompt config."""
    # Valid config
    valid_config = PromptConfig({
        "prompt": {
            "config_info": {
                "name": "test_prompts",
                "description": "Test configuration",
                "version": "1.0"
            },
            "prompts": [{
                "name": "test_prompt",
                "text": "Test prompt",
                "category": "test",
                "field_to_extract": "test"
            }]
        }
    })
    assert valid_config.validate() is True

    # Invalid config
    with pytest.raises(ValueError):
        PromptConfig({}).validate()

def test_evaluation_config_validation():
    """Test validation of evaluation config."""
    # Valid config
    valid_config = EvaluationConfig({
        "evaluation": {
            "metrics": ["accuracy"],
            "dataset": {"path": "test"},
            "output": {"format": "json"}
        }
    })
    assert valid_config.validate() is True

    # Invalid config
    with pytest.raises(ValueError):
        EvaluationConfig({}).validate() 