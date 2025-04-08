"""
Locational prompt generator that helps direct attention to specific areas of an image.
"""
from typing import Any, Dict, List, Tuple, Optional

from src.prompts.base_prompt_generator import BasePromptGenerator


class LocationalPromptGenerator(BasePromptGenerator):
    """
    A prompt generator that provides location information to help the model
    locate specific areas of interest in an image or document.
    """
    
    def __init__(self, config, field: str):
        """
        Initialize the locational prompt generator.
        
        Args:
            config: Configuration containing prompt templates and location info
            field: The specific field in config that contains this prompt's template
        """
        self.config = config
        self.field = field
        self.template = self.config.get_template(field)
        self.location_descriptions = self.config.get_locations(field)
        
        if not self.template:
            raise ValueError(f"Template for field '{field}' not found in configuration")
    
    def _format_location_descriptions(self, data: Dict[str, Any]) -> str:
        """
        Format the location descriptions with data where applicable.
        
        Args:
            data: Dictionary containing values to be inserted into location descriptions
            
        Returns:
            str: The formatted location descriptions
        """
        if not self.location_descriptions:
            return ""
        
        try:
            # If it's a string, format it directly
            if isinstance(self.location_descriptions, str):
                return self.location_descriptions.format(**data)
            
            # If it's a list, format each description
            if isinstance(self.location_descriptions, list):
                formatted_locations = []
                for i, location in enumerate(self.location_descriptions):
                    formatted_location = location.format(**data)
                    formatted_locations.append(f"Location {i+1}: {formatted_location}")
                return "\n".join(formatted_locations)
                
            # If it's a dict, format each key-value pair
            if isinstance(self.location_descriptions, dict):
                formatted_locations = []
                for loc_name, loc_desc in self.location_descriptions.items():
                    formatted_desc = loc_desc.format(**data)
                    formatted_locations.append(f"{loc_name}: {formatted_desc}")
                return "\n".join(formatted_locations)
                
            return str(self.location_descriptions)
            
        except KeyError:
            return ""
    
    def generate_prompt(self, data: Dict[str, Any]) -> str:
        """
        Generate a prompt with location information about where to find data in an image.
        
        Args:
            data: Dictionary containing values to be inserted into the template
            
        Returns:
            str: The formatted prompt with location information
        """
        try:
            # Format the main instruction template
            instruction = self.template.format(**data)
            
            # Add location information if available
            location_info = self._format_location_descriptions(data)
            
            # Combine instruction with location information
            if location_info:
                return f"{instruction}\n\nLocation Information:\n{location_info}"
            else:
                return instruction
                
        except KeyError as e:
            raise ValueError(f"Missing required data field: {e}")
        except Exception as e:
            raise ValueError(f"Error generating locational prompt: {e}")
