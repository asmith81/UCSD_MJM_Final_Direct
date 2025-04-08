"""
Step-by-step prompt generator that breaks down tasks into sequential steps.
"""
from typing import Any, Dict, List

from src.prompts.base_prompt_generator import BasePromptGenerator


class StepByStepPromptGenerator(BasePromptGenerator):
    """
    A prompt generator that breaks down a complex task into sequential steps,
    guiding the model to solve problems step-by-step.
    """
    
    def __init__(self, config, field: str):
        """
        Initialize the step-by-step prompt generator.
        
        Args:
            config: Configuration containing prompt templates and steps
            field: The specific field in config containing this prompt's template
        """
        self.config = config
        self.field = field
        self.introduction = self.config.get_introduction(field)
        self.steps = self.config.get_steps(field)
        self.conclusion = self.config.get_conclusion(field)
        
        if not self.steps or not isinstance(self.steps, list):
            raise ValueError(f"Steps for field '{field}' not found or invalid format")
    
    def generate_prompt(self, data: Dict[str, Any]) -> str:
        """
        Generate a prompt that guides the model through steps to solve a problem.
        
        Args:
            data: Dictionary containing values to be inserted into the steps
            
        Returns:
            str: The formatted step-by-step prompt
        """
        try:
            prompt_parts = []
            
            # Add introduction if available
            if self.introduction:
                intro_text = self.introduction.format(**data)
                prompt_parts.append(intro_text)
            
            # Add numbered steps
            steps_text = []
            for i, step in enumerate(self.steps):
                formatted_step = step.format(**data)
                steps_text.append(f"Step {i+1}: {formatted_step}")
            
            prompt_parts.append("\n".join(steps_text))
            
            # Add conclusion if available
            if self.conclusion:
                conclusion_text = self.conclusion.format(**data)
                prompt_parts.append(conclusion_text)
            
            # Combine all parts
            return "\n\n".join(prompt_parts)
            
        except KeyError as e:
            raise ValueError(f"Missing required data field: {e}")
        except Exception as e:
            raise ValueError(f"Error generating step-by-step prompt: {e}")
