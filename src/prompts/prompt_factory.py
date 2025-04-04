"""
Factory for creating prompt generators.
"""
from typing import Dict, Type, Any

from .base_prompt_generator import BasePromptGenerator
from .strategies.basic_prompt import BasicPromptGenerator
from .strategies.detailed_prompt import DetailedPromptGenerator
from .strategies.few_shot_prompt import FewShotPromptGenerator
from .strategies.locational_prompt import LocationalPromptGenerator
from .strategies.step_by_step_prompt import StepByStepPromptGenerator
from ..config import get_config_manager, ConfigType

class PromptFactory:
    """
    Factory for creating prompt generators based on configuration.
    Uses dependency injection and configuration management.
    """

    # Registry of available prompt strategies
    PROMPT_REGISTRY: Dict[str, Type[BasePromptGenerator]] = {
        "basic": BasicPromptGenerator,
        "detailed": DetailedPromptGenerator,
        "few_shot": FewShotPromptGenerator,
        "locational": LocationalPromptGenerator,
        "step_by_step": StepByStepPromptGenerator
    }

    def create_prompt_generator(self, prompt_name: str, field: str) -> BasePromptGenerator:
        """
        Create a prompt generator for a specific field.

        Args:
            prompt_name: Name of the prompt configuration to use
            field: Field to extract (e.g., "work_order", "cost")

        Returns:
            BasePromptGenerator: The initialized prompt generator

        Raises:
            ValueError: If prompt type is not supported
            ConfigurationError: If prompt configuration is invalid
        """
        # Load prompt configuration
        config_manager = get_config_manager()
        prompt_config = config_manager.get_config(ConfigType.PROMPT, prompt_name)

        # Get prompts for the specified field
        field_prompts = prompt_config.get_prompts_by_field(field)
        if not field_prompts:
            raise ValueError(f"No prompts found for field: {field}")

        # Get prompt type from configuration
        prompt_type = field_prompts[0].get("category")
        if not prompt_type or prompt_type not in self.PROMPT_REGISTRY:
            raise ValueError(f"Unsupported prompt type: {prompt_type}")

        # Create prompt generator with configuration
        generator_class = self.PROMPT_REGISTRY[prompt_type]
        return generator_class(prompt_config, field)

    @classmethod
    def register_prompt_generator(cls, prompt_type: str, generator_class: Type[BasePromptGenerator]):
        """
        Register a new prompt generator implementation.

        Args:
            prompt_type: Type identifier for the prompt generator
            generator_class: Generator class implementing BasePromptGenerator
        """
        cls.PROMPT_REGISTRY[prompt_type] = generator_class
