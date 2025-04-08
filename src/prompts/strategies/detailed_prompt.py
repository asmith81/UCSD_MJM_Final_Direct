"""
Detailed prompt generator that provides more structured and comprehensive prompts.
"""
from typing import Any, Dict, List

from src.prompts.base_prompt_generator import BasePromptGenerator


class DetailedPromptGenerator(BasePromptGenerator):
    """
    A prompt generator that creates detailed, structured prompts with sections for
    context, instructions, examples, and specific requirements.
    """
    
    def __init__(self, config, field: str):
        """
        Initialize the detailed prompt generator.
        
        Args:
            config: Configuration containing prompt templates and sections
            field: The specific field/key in config that contains this prompt's template
        """
        self.config = config
        self.field = field
        self.sections = self.config.get_sections(field)
        
        if not self.sections:
            raise ValueError(f"Detailed sections for field '{field}' not found in configuration")
        
        # Validate required sections
        self._validate_sections()
    
    def _validate_sections(self):
        """
        Validate that required sections are present in the configuration.
        
        Raises:
            ValueError: If required sections are missing
        """
        required_sections = ["instructions", "context"]
        missing_sections = [section for section in required_sections if section not in self.sections]
        
        if missing_sections:
            raise ValueError(f"Missing required sections for detailed prompt: {', '.join(missing_sections)}")
    
    def generate_prompt(self, data: Dict[str, Any]) -> str:
        """
        Generate a structured prompt from all sections in the configuration.
        
        Args:
            data: Dictionary containing values to be inserted into each section
            
        Returns:
            str: The formatted detailed prompt
        """
        try:
            prompt_parts = []
            
            # Add context section
            if "context" in self.sections:
                context = self.sections["context"].format(**data)
                prompt_parts.append(f"Context:\n{context}\n")
            
            # Add instructions section
            if "instructions" in self.sections:
                instructions = self.sections["instructions"].format(**data)
                prompt_parts.append(f"Instructions:\n{instructions}\n")
            
            # Add examples section if available
            if "examples" in self.sections:
                examples = self.sections["examples"].format(**data)
                prompt_parts.append(f"Examples:\n{examples}\n")
            
            # Add requirements section if available
            if "requirements" in self.sections:
                requirements = self.sections["requirements"].format(**data)
                prompt_parts.append(f"Requirements:\n{requirements}\n")
            
            # Add custom sections
            for section_name, section_content in self.sections.items():
                if section_name not in ["context", "instructions", "examples", "requirements"]:
                    formatted_content = section_content.format(**data)
                    prompt_parts.append(f"{section_name.capitalize()}:\n{formatted_content}\n")
            
            # Combine all sections
            return "\n".join(prompt_parts)
            
        except KeyError as e:
            raise ValueError(f"Missing required data field: {e}")
        except Exception as e:
            raise ValueError(f"Error generating detailed prompt: {e}")
