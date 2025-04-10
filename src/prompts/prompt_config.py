"""Configuration for prompt generators.

This module provides the configuration class for prompt generators,
handling prompt templates and validation rules.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from src.config.base_config import BaseConfig


@dataclass
class PromptTemplate:
    """Structure for a single prompt template.
    
    Attributes:
        name: Unique identifier for the prompt
        text: The prompt template text
        category: Category of the prompt (basic, detailed, positioned)
        field_to_extract: Field this prompt is designed to extract
        description: Description of the prompt's purpose
        version: Version of the prompt template
        format_instructions: Optional formatting instructions
        metadata: Additional metadata about the prompt
    """
    name: str
    text: str
    category: str
    field_to_extract: str
    description: Optional[str] = None
    version: Optional[str] = None
    format_instructions: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PromptConfig(BaseConfig):
    """Configuration for prompt generators.
    
    This class handles configuration for prompt generators, including
    loading and validating prompt templates.
    
    Attributes:
        prompts: List of prompt templates
        metadata: Configuration metadata
    """
    
    def __init__(
        self,
        prompts: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize prompt configuration.
        
        Args:
            prompts: List of prompt template configurations
            metadata: Configuration metadata
        """
        self.prompts = [PromptTemplate(**p) for p in prompts]
        self.metadata = metadata or {}
        
    def get_prompts_by_field(self, field_type: str) -> List[PromptTemplate]:
        """Get all prompts for a specific field type.
        
        Args:
            field_type: Type of field to get prompts for
            
        Returns:
            List of prompt templates for the field
        """
        return [p for p in self.prompts if p.field_to_extract == field_type]
        
    def get_prompt_by_name(self, name: str) -> Optional[PromptTemplate]:
        """Get a specific prompt template by name.
        
        Args:
            name: Name of the prompt template
            
        Returns:
            The prompt template or None if not found
        """
        for prompt in self.prompts:
            if prompt.name == name:
                return prompt
        return None
        
    def get_section(self, section_name: str) -> Dict[str, Any]:
        """Get a configuration section.
        
        Args:
            section_name: Name of the section to retrieve
            
        Returns:
            Dictionary containing the section data
        """
        if section_name == "prompts":
            return {"prompts": [vars(p) for p in self.prompts]}
        elif section_name == "metadata":
            return {"metadata": self.metadata}
        return {}
        
    def get_value(self, key: str) -> Any:
        """Get a configuration value.
        
        Args:
            key: Key to retrieve value for
            
        Returns:
            Value associated with the key
        """
        if key in self.metadata:
            return self.metadata[key]
        return None
        
    def validate(self) -> bool:
        """Validate the configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        if not self.prompts:
            return False
        
        for prompt in self.prompts:
            if not all([
                prompt.name,
                prompt.text,
                prompt.category,
                prompt.field_to_extract
            ]):
                return False
        return True

    def get_data(self) -> Dict[str, Any]:
        """Get the complete configuration data.
        
        Returns:
            Dictionary containing all configuration data including prompts and metadata
        """
        return {
            "prompts": [vars(p) for p in self.prompts],
            "metadata": self.metadata
        } 