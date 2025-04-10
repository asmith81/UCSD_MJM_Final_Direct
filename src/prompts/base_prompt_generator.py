"""
Base class for prompt generators.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict

class BasePromptGenerator(ABC):
    """
    Abstract base class for prompt generators.
    Defines the interface that all prompt generator strategies must implement.
    """
    
    @abstractmethod
    def __init__(self, config, field: str):
        """
        Initialize the prompt generator.
        
        Args:
            config: The configuration containing prompt templates
            field: The field this prompt generator is responsible for
        """
        pass
        
    @abstractmethod
    def generate_prompt(self, data: Dict[str, Any]) -> str:
        """
        Generate a prompt using the configured template and provided data.
        
        Args:
            data: Data to be used in the prompt generation
            
        Returns:
            str: The generated prompt
        """
        pass
