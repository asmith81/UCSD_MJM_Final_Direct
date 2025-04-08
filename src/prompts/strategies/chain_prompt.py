"""
Chain prompt generator that combines multiple prompts.
"""
from typing import Any, Dict, List

from src.prompts.base_prompt_generator import BasePromptGenerator


class ChainPromptGenerator(BasePromptGenerator):
    """
    A prompt generator that chains multiple prompt generators together.
    Each generator in the chain adds its output to a combined prompt.
    """
    
    def __init__(self, config, field: str):
        """
        Initialize the chain prompt generator.
        
        Args:
            config: Configuration containing prompt templates and chain configuration
            field: The specific field/key in config that contains chain configuration
        """
        self.config = config
        self.field = field
        self.chain_config = self.config.get(field)
        
        if not self.chain_config or not isinstance(self.chain_config, list):
            raise ValueError(f"Chain configuration for field '{field}' not found or is not a list")
        
        self.generators: List[BasePromptGenerator] = []
        for generator_config in self.chain_config:
            if not isinstance(generator_config, dict):
                raise ValueError(f"Invalid generator configuration: {generator_config}")
            
            generator_type = generator_config.get("type")
            generator_field = generator_config.get("field")
            
            if not generator_type or not generator_field:
                raise ValueError("Generator configuration must include 'type' and 'field'")
            
            # Import the appropriate generator class based on type
            try:
                generator_module = __import__(f"src.prompts.strategies.{generator_type}", fromlist=[""])
                generator_class = getattr(generator_module, f"{generator_type.capitalize()}PromptGenerator")
                self.generators.append(generator_class(self.config, generator_field))
            except (ImportError, AttributeError) as e:
                raise ValueError(f"Failed to import generator type '{generator_type}': {e}")
    
    def generate_prompt(self, data: Dict[str, Any]) -> str:
        """
        Generate a prompt by chaining all the prompt generators.
        
        Args:
            data: Dictionary containing values to be inserted into the templates
            
        Returns:
            str: The combined prompt from all generators in the chain
        """
        if not self.generators:
            return ""
        
        result = []
        for generator in self.generators:
            try:
                result.append(generator.generate_prompt(data))
            except Exception as e:
                raise ValueError(f"Error in chain prompt generation: {e}")
        
        return "\n\n".join(result) 