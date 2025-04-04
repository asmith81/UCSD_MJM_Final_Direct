"""
Factory class for creating configuration objects.
"""
from typing import Dict, Any
from .base_config import BaseConfig
from .implementations.model_config import ModelConfig
from .implementations.prompt_config import PromptConfig
from .implementations.evaluation_config import EvaluationConfig


class ConfigFactory:
    """
    Factory class for creating configuration objects.
    Handles the creation of specific configuration types based on the data provided.
    """

    def create_model_config(self, data: Dict[str, Any]) -> BaseConfig:
        """
        Create a model configuration object.
        
        Args:
            data (Dict[str, Any]): Raw configuration data
            
        Returns:
            BaseConfig: A ModelConfig instance implementing BaseConfig
        """
        return ModelConfig(data)

    def create_prompt_config(self, data: Dict[str, Any]) -> BaseConfig:
        """
        Create a prompt configuration object.
        
        Args:
            data (Dict[str, Any]): Raw configuration data
            
        Returns:
            BaseConfig: A PromptConfig instance implementing BaseConfig
        """
        return PromptConfig(data)

    def create_evaluation_config(self, data: Dict[str, Any]) -> BaseConfig:
        """
        Create an evaluation configuration object.
        
        Args:
            data (Dict[str, Any]): Raw configuration data
            
        Returns:
            BaseConfig: An EvaluationConfig instance implementing BaseConfig
        """
        return EvaluationConfig(data) 