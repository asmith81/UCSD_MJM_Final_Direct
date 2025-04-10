"""
Factory for creating prompt generators.

This module provides the PromptFactory class for creating prompt generators
based on configuration. It handles loading prompt templates and creating
appropriate generators for different field types and strategies.
"""
from typing import Dict, Type, Any, Optional, List
from pathlib import Path
import yaml
import re
from decimal import Decimal

from .base_prompt_generator import BasePromptGenerator
from .prompt_config import PromptConfig
from ..config.base_config import BaseConfig
from ..data.validators.field_validators import validate_total_amount, validate_work_order

# Import all available prompt generators
from .strategies.basic_prompt import BasicPromptGenerator
from .strategies.detailed_prompt import DetailedPromptGenerator
from .strategies.locational_prompt import LocationalPromptGenerator
from .strategies.few_shot_prompt import FewShotPromptGenerator
from .strategies.step_by_step_prompt import StepByStepPromptGenerator
from .strategies.template_prompt import TemplatePromptGenerator


class PromptFactoryError(Exception):
    """Base exception for prompt factory errors."""
    pass


class PromptConfigError(PromptFactoryError):
    """Raised when prompt configuration is invalid."""
    pass


class PromptGeneratorError(PromptFactoryError):
    """Raised when generator creation or initialization fails."""
    pass


class PromptFactory:
    """
    Factory for creating prompt generators based on configuration.
    Uses dependency injection and configuration management.
    """
    
    # Registry for prompt generator implementations
    REGISTRY: Dict[str, Type[BasePromptGenerator]] = {}
    
    # Valid prompt categories
    VALID_CATEGORIES = {'basic', 'detailed', 'positioned', 'few_shot', 'step_by_step', 'template'}
    
    # Valid field types (based on ground truth requirements)
    VALID_FIELD_TYPES = {'work_order', 'cost'}
    
    # Field-specific format requirements
    FIELD_REQUIREMENTS = {
        'work_order': {
            'type': str,
            'validation': lambda x: bool(re.match(r'^\d{5}$', x)),
            'format_description': "5 alphanumeric characters"
        },
        'cost': {
            'type': Decimal,
            'validation': lambda x: float(x) > 0 and len(str(float(x)).split('.')[1]) <= 2,
            'format_description': "Positive number with up to 2 decimal places"
        }
    }
    
    # Track active generators for cleanup
    _active_generators: List[BasePromptGenerator] = []
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the factory with required dependencies.
        
        Args:
            config_dir: Optional directory containing prompt configurations
            
        Raises:
            ValueError: If config_dir is None
        """
        if config_dir is None:
            raise ValueError("config_dir is required")
        self.config_dir = config_dir
        self._register_default_generators()
        
    def _register_default_generators(self) -> None:
        """Register the default set of prompt generators."""
        try:
            self.register_generator('basic', BasicPromptGenerator)
            self.register_generator('detailed', DetailedPromptGenerator)
            self.register_generator('positioned', LocationalPromptGenerator)
            self.register_generator('few_shot', FewShotPromptGenerator)
            self.register_generator('step_by_step', StepByStepPromptGenerator)
            self.register_generator('template', TemplatePromptGenerator)
        except Exception as e:
            raise PromptFactoryError(f"Failed to register default generators: {str(e)}")
        
    @classmethod
    def register_generator(
        cls,
        category: str,
        generator_class: Type[BasePromptGenerator]
    ) -> None:
        """Register a new prompt generator implementation.
        
        Args:
            category: Category identifier for the generator
            generator_class: Class implementing BasePromptGenerator
            
        Raises:
            ValueError: If category is invalid or already registered
            TypeError: If generator_class doesn't implement BasePromptGenerator
        """
        if category not in cls.VALID_CATEGORIES:
            raise ValueError(f"Invalid category: {category}")
            
        if not issubclass(generator_class, BasePromptGenerator):
            raise TypeError(
                f"Generator class must implement BasePromptGenerator"
            )
            
        registry_key = category
        if registry_key in cls.REGISTRY:
            raise ValueError(f"Category already registered: {category}")
            
        cls.REGISTRY[registry_key] = generator_class
        
    def create_generator(
        self,
        category: str,
        field_type: str,
        config: Optional[BaseConfig] = None
    ) -> BasePromptGenerator:
        """Create a prompt generator instance.
        
        Args:
            category: Type of generator to create ('basic', 'detailed', etc.)
            field_type: Type of field to extract ('work_order', 'cost')
            config: Optional configuration for the generator
            
        Returns:
            BasePromptGenerator: The created generator instance
            
        Raises:
            ValueError: If category or field_type is invalid
            PromptFactoryError: If generator creation fails
        """
        # Validate inputs
        if category not in self.VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category: {category}. Must be one of {self.VALID_CATEGORIES}"
            )
            
        if field_type not in self.VALID_FIELD_TYPES:
            raise ValueError(
                f"Invalid field type: {field_type}. Must be one of {self.VALID_FIELD_TYPES}"
            )
            
        # Get the generator class
        registry_key = category
        if registry_key not in self.REGISTRY:
            raise PromptFactoryError(f"No generator registered for category: {category}")
            
        generator_class = self.REGISTRY[registry_key]
        
        try:
            # Create generator instance
            generator = generator_class()
            
            # Load configuration if not provided
            if config is None:
                config = self._load_config(category, field_type)
                
            # Validate configuration
            if not self._validate_config(config, category, field_type):
                raise PromptConfigError("Invalid configuration for prompt generator")
                
            # Initialize the generator
            generator.initialize(config)
            
            # Track for cleanup
            self._active_generators.append(generator)
            
            return generator
            
        except Exception as e:
            raise PromptGeneratorError(f"Failed to create generator: {str(e)}") from e
            
    def _validate_config(self, config: BaseConfig, category: str, field_type: str) -> bool:
        """Validate configuration for a prompt generator.
        
        Args:
            config: Configuration to validate
            category: Generator category
            field_type: Field type to extract
            
        Returns:
            bool: True if configuration is valid
            
        Raises:
            PromptConfigError: If validation fails with specific reason
        """
        try:
            if not isinstance(config, PromptConfig):
                raise PromptConfigError("Configuration must be a PromptConfig instance")
                
            # Validate prompts exist for the field type
            field_prompts = [p for p in config.prompts if p.field_to_extract == field_type]
            if not field_prompts:
                raise PromptConfigError(f"No prompts found for field type: {field_type}")
                
            # Get field requirements
            field_reqs = self.FIELD_REQUIREMENTS.get(field_type)
            if not field_reqs:
                raise PromptConfigError(f"No requirements defined for field type: {field_type}")
                
            # Validate each prompt has required fields and format instructions
            for prompt in field_prompts:
                # Basic field validation
                if not prompt.name or not prompt.text or not prompt.category:
                    raise PromptConfigError("Prompts must have name, text, and category")
                if prompt.category != category:
                    raise PromptConfigError(f"Prompt category mismatch: {prompt.category} != {category}")
                    
                # Validate format instructions exist and match field requirements
                if not prompt.format_instructions:
                    prompt.format_instructions = field_reqs['format_description']
                elif field_reqs['format_description'] not in prompt.format_instructions:
                    prompt.format_instructions = f"{prompt.format_instructions}\n{field_reqs['format_description']}"
                    
                # Validate any example values in the prompt match the field requirements
                if prompt.metadata and 'examples' in prompt.metadata:
                    for example in prompt.metadata['examples']:
                        if 'output' in example:
                            output = example['output']
                            # Validate example matches field type requirements
                            if field_type == 'work_order':
                                is_valid, error_msg, _ = validate_work_order(output)
                                if not is_valid:
                                    raise PromptConfigError(
                                        f"Invalid work order example: {output}. {error_msg}"
                                    )
                            elif field_type == 'cost':
                                is_valid, error_msg, _ = validate_total_amount(output)
                                if not is_valid:
                                    raise PromptConfigError(
                                        f"Invalid cost example: {output}. {error_msg}"
                                    )
                    
            return True
            
        except Exception as e:
            raise PromptConfigError(f"Configuration validation failed: {str(e)}")
            
    def _load_config(self, category: str, field_type: str) -> BaseConfig:
        """Load configuration for a prompt generator.
        
        Args:
            category: Generator category
            field_type: Field type to extract
            
        Returns:
            BaseConfig: Configuration for the generator
            
        Raises:
            PromptFactoryError: If configuration loading fails
        """
        try:
            # Load the appropriate YAML file
            config_file = self.config_dir / f"{category}.yaml"
            
            if not config_file.exists():
                raise FileNotFoundError(f"Config file not found: {config_file}")
                
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
                
            # Filter prompts for the specific field type
            field_prompts = [
                p for p in config_data.get('prompts', [])
                if p.get('field_to_extract') == field_type
            ]
            
            if not field_prompts:
                raise ValueError(f"No prompts found for field type: {field_type}")
                
            # Create configuration object
            return PromptConfig(
                prompts=field_prompts,
                metadata=config_data.get('config_info', {})
            )
            
        except Exception as e:
            raise PromptFactoryError(f"Failed to load config: {str(e)}") from e
            
    def cleanup(self) -> None:
        """Clean up resources used by active generators."""
        for generator in self._active_generators:
            try:
                generator.cleanup()
            except Exception as e:
                # Log but don't raise, to ensure all generators are cleaned up
                print(f"Warning: Failed to cleanup generator: {str(e)}")
        self._active_generators.clear()
