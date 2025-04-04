"""
Configuration loader for YAML configuration files.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Protocol

from .base_config import BaseConfig
from .config_factory import ConfigFactory


class ConfigParser(Protocol):
    """Protocol for configuration file parsers."""
    
    def load(self, file_path: Path) -> Dict[str, Any]:
        """
        Load and parse a configuration file.
        
        Args:
            file_path: Path to configuration file
            
        Returns:
            Dict[str, Any]: Parsed configuration data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If parsing fails
        """
        ...


class YAMLConfigParser:
    """YAML configuration file parser."""
    
    def load(self, file_path: Path) -> Dict[str, Any]:
        """
        Load and parse a YAML configuration file.
        
        Args:
            file_path: Path to YAML file
            
        Returns:
            Dict[str, Any]: Parsed YAML data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        import yaml
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
            
        with open(file_path, 'r') as f:
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise yaml.YAMLError(f"Error parsing YAML file {file_path}: {str(e)}")


class ConfigLoader:
    """
    Loads and validates configuration files.
    Uses dependency injection for configuration factory, parser, and paths.
    """

    def __init__(self, config_path: Path, config_factory: ConfigFactory, config_parser: ConfigParser = None):
        """
        Initialize the configuration loader.
        
        Args:
            config_path: Base path to configuration files
            config_factory: Factory for creating config objects
            config_parser: Parser for configuration files (defaults to YAMLConfigParser)
        """
        self.config_path = config_path
        self.config_factory = config_factory
        self.config_parser = config_parser or YAMLConfigParser()

    def load_model_config(self, model_name: str) -> BaseConfig:
        """
        Load model configuration from file.
        
        Args:
            model_name: Name of the model configuration to load
            
        Returns:
            BaseConfig: Configuration object implementing BaseConfig
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            ValueError: If parsing fails
        """
        config_file = self.config_path / "models" / f"{model_name}.yaml"
        data = self.config_parser.load(config_file)
        return self.config_factory.create_model_config(data)

    def load_prompt_config(self, prompt_type: str) -> BaseConfig:
        """
        Load prompt configuration from file.
        
        Args:
            prompt_type: Type of prompt configuration to load
            
        Returns:
            BaseConfig: Configuration object implementing BaseConfig
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            ValueError: If parsing fails
        """
        config_file = self.config_path / "prompts" / f"{prompt_type}.yaml"
        data = self.config_parser.load(config_file)
        return self.config_factory.create_prompt_config(data)

    def load_evaluation_config(self) -> BaseConfig:
        """
        Load evaluation configuration from file.
        
        Returns:
            BaseConfig: Configuration object implementing BaseConfig
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            ValueError: If parsing fails
        """
        config_file = self.config_path / "evaluation.yaml"
        data = self.config_parser.load(config_file)
        return self.config_factory.create_evaluation_config(data)
