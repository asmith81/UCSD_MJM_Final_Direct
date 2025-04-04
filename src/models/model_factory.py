"""
Factory for creating model instances.
"""
from typing import Dict, Type, Any

from .base_model import BaseModel
from .implementations.doctr_model import DoctrModel
from .implementations.llama_vision_model import LlamaVisionModel
from .implementations.pixtral_model import PixtralModel
from ..config import get_config_manager, ConfigType

class ModelFactory:
    """
    Factory for creating model instances based on configuration.
    Uses dependency injection and configuration management.
    """

    # Registry of available model implementations
    MODEL_REGISTRY: Dict[str, Type[BaseModel]] = {
        "doctr": DoctrModel,
        "llama_vision": LlamaVisionModel,
        "pixtral": PixtralModel
    }

    def create_model(self, model_name: str) -> BaseModel:
        """
        Create a model instance based on configuration.

        Args:
            model_name: Name of the model configuration to use

        Returns:
            BaseModel: The initialized model instance

        Raises:
            ValueError: If model type is not supported
            ConfigurationError: If model configuration is invalid
        """
        # Load model configuration
        config_manager = get_config_manager()
        model_config = config_manager.get_config(ConfigType.MODEL, model_name)

        # Get model type from configuration
        model_type = model_config.get_value("type")
        if not model_type or model_type not in self.MODEL_REGISTRY:
            raise ValueError(f"Unsupported model type: {model_type}")

        # Create model instance with configuration
        model_class = self.MODEL_REGISTRY[model_type]
        return model_class(model_config)

    @classmethod
    def register_model(cls, model_type: str, model_class: Type[BaseModel]):
        """
        Register a new model implementation.

        Args:
            model_type: Type identifier for the model
            model_class: Model class implementing BaseModel
        """
        cls.MODEL_REGISTRY[model_type] = model_class
