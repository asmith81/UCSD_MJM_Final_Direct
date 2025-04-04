"""
Tests for the ConfigLoader class.
"""
import os
import pytest
import yaml
from pathlib import Path
from typing import Dict, Any
from src.config.config_loader import ConfigLoader, ConfigParser, YAMLConfigParser
from src.config.config_factory import ConfigFactory
from src.config.base_config import BaseConfig

class MockConfigParser:
    """Mock configuration parser for testing."""
    def load(self, file_path: Path) -> Dict[str, Any]:
        """Mock load method that returns predefined data."""
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        if file_path.name == "invalid.yaml":
            raise ValueError("Mock parsing error")
        
        # Return appropriate structure based on file path
        if "models" in str(file_path):
            return {
                "model": {
                    "name": "test_model",
                    "type": "mock",
                    "parameters": {"mock_param": "value"}
                }
            }
        elif "prompts" in str(file_path):
            return {
                "prompt": {
                    "config_info": {"name": "test_prompt"},
                    "prompts": [{"name": "test", "text": "mock"}]
                }
            }
        elif "evaluation.yaml" in str(file_path):
            return {
                "evaluation": {
                    "metrics": ["mock_metric"],
                    "dataset": {"path": "mock_path"},
                    "output": {"format": "mock"}
                }
            }
        return {"error": "Unknown file type"}

@pytest.fixture
def config_path(tmp_path) -> Path:
    """Create a temporary config directory with test files."""
    # Create config structure
    models_dir = tmp_path / "models"
    prompts_dir = tmp_path / "prompts"
    models_dir.mkdir()
    prompts_dir.mkdir()
    
    # Create test model config
    model_config = {
        "model": {
            "name": "test_model",
            "type": "llm",
            "parameters": {"param1": "value1"}
        }
    }
    with open(models_dir / "test_model.yaml", "w") as f:
        yaml.dump(model_config, f)
    
    # Create test prompt config
    prompt_config = {
        "prompt": {
            "config_info": {
                "name": "test_prompts",
                "version": "1.0"
            },
            "prompts": [{
                "name": "test_prompt",
                "text": "Test prompt text",
                "category": "test",
                "field_to_extract": "test_field"
            }]
        }
    }
    with open(prompts_dir / "test_prompt.yaml", "w") as f:
        yaml.dump(prompt_config, f)
    
    # Create test evaluation config
    eval_config = {
        "evaluation": {
            "metrics": ["accuracy"],
            "dataset": {"path": "test_path"},
            "output": {"format": "json"}
        }
    }
    with open(tmp_path / "evaluation.yaml", "w") as f:
        yaml.dump(eval_config, f)
    
    return tmp_path

@pytest.fixture
def config_loader(config_path) -> ConfigLoader:
    """Create a ConfigLoader instance with test configuration."""
    return ConfigLoader(config_path, ConfigFactory())

@pytest.fixture
def mock_config_loader(config_path) -> ConfigLoader:
    """Create a ConfigLoader instance with mock parser."""
    return ConfigLoader(config_path, ConfigFactory(), MockConfigParser())

def test_config_loader_initialization(config_path):
    """Test ConfigLoader initialization."""
    factory = ConfigFactory()
    parser = YAMLConfigParser()
    loader = ConfigLoader(config_path, factory, parser)
    
    assert loader.config_path == config_path
    assert loader.config_factory == factory
    assert loader.config_parser == parser

def test_config_loader_default_parser(config_path):
    """Test ConfigLoader uses default YAML parser."""
    loader = ConfigLoader(config_path, ConfigFactory())
    assert isinstance(loader.config_parser, YAMLConfigParser)

def test_load_model_config(config_loader):
    """Test loading model configuration."""
    config = config_loader.load_model_config("test_model")
    
    assert isinstance(config, BaseConfig)
    data = config.get_data()
    assert "name" in data
    assert "type" in data
    assert "parameters" in data
    assert data["name"] == "test_model"
    assert data["type"] == "llm"
    assert data["parameters"]["param1"] == "value1"

def test_load_prompt_config(config_loader):
    """Test loading prompt configuration."""
    config = config_loader.load_prompt_config("test_prompt")
    
    assert isinstance(config, BaseConfig)
    data = config.get_data()
    assert "config_info" in data
    assert "prompts" in data
    assert data["config_info"]["name"] == "test_prompts"
    assert len(data["prompts"]) == 1
    prompt = data["prompts"][0]
    assert prompt["name"] == "test_prompt"
    assert prompt["field_to_extract"] == "test_field"

def test_load_evaluation_config(config_loader):
    """Test loading evaluation configuration."""
    config = config_loader.load_evaluation_config()
    
    assert isinstance(config, BaseConfig)
    data = config.get_data()
    assert "metrics" in data
    assert "dataset" in data
    assert "output" in data
    assert data["metrics"] == ["accuracy"]
    assert data["dataset"]["path"] == "test_path"
    assert data["output"]["format"] == "json"

def test_nonexistent_model_config(config_loader):
    """Test error handling for nonexistent model config."""
    with pytest.raises(FileNotFoundError) as exc_info:
        config_loader.load_model_config("nonexistent")
    assert "not found" in str(exc_info.value)

def test_nonexistent_prompt_config(config_loader):
    """Test error handling for nonexistent prompt config."""
    with pytest.raises(FileNotFoundError) as exc_info:
        config_loader.load_prompt_config("nonexistent")
    assert "not found" in str(exc_info.value)

def test_invalid_yaml_model_config(config_loader, config_path):
    """Test error handling for invalid YAML in model config."""
    # Create invalid YAML file
    invalid_yaml = "invalid: yaml: :"
    with open(config_path / "models" / "invalid.yaml", "w") as f:
        f.write(invalid_yaml)
    
    with pytest.raises(yaml.YAMLError) as exc_info:
        config_loader.load_model_config("invalid")
    assert "Error parsing YAML file" in str(exc_info.value)

def test_invalid_yaml_prompt_config(config_loader, config_path):
    """Test error handling for invalid YAML in prompt config."""
    # Create invalid YAML file
    invalid_yaml = "invalid: yaml: :"
    with open(config_path / "prompts" / "invalid.yaml", "w") as f:
        f.write(invalid_yaml)
    
    with pytest.raises(yaml.YAMLError) as exc_info:
        config_loader.load_prompt_config("invalid")
    assert "Error parsing YAML file" in str(exc_info.value)

def test_missing_evaluation_config(config_loader, config_path):
    """Test error handling for missing evaluation config."""
    # Remove evaluation.yaml
    (config_path / "evaluation.yaml").unlink()
    
    with pytest.raises(FileNotFoundError) as exc_info:
        config_loader.load_evaluation_config()
    assert "not found" in str(exc_info.value)

def test_mock_parser_integration(mock_config_loader):
    """Test integration with mock parser."""
    config = mock_config_loader.load_model_config("test_model")
    data = config.get_data()
    assert data["name"] == "test_model"
    assert data["type"] == "mock"
    assert data["parameters"]["mock_param"] == "value" 