"""
Few-shot prompt generator that includes examples in the prompt.
"""
from typing import Any, Dict, List

from src.prompts.base_prompt_generator import BasePromptGenerator


class FewShotPromptGenerator(BasePromptGenerator):
    """
    A prompt generator that includes examples/demonstrations in the prompt to help
    the model understand the task through few-shot learning.
    """
    
    def __init__(self, config, field: str):
        """
        Initialize the few-shot prompt generator.
        
        Args:
            config: Configuration containing prompt templates and examples
            field: The specific field in config that contains this prompt's template
        """
        self.config = config
        self.field = field
        self.template = self.config.get_template(field)
        self.examples = self.config.get_examples(field)
        
        if not self.template:
            raise ValueError(f"Template for field '{field}' not found in configuration")
        
        if not self.examples or not isinstance(self.examples, list):
            raise ValueError(f"Examples for field '{field}' not found or invalid format")
    
    def _format_examples(self, data: Dict[str, Any]) -> str:
        """
        Format the examples with data where applicable.
        
        Args:
            data: Dictionary containing values to be inserted into examples
            
        Returns:
            str: The formatted examples section
        """
        formatted_examples = []
        
        for i, example in enumerate(self.examples):
            try:
                # If example is a string, format it directly
                if isinstance(example, str):
                    formatted_example = example.format(**data)
                # If example is a dict, format input and output separately
                elif isinstance(example, dict):
                    input_text = example.get("input", "").format(**data)
                    output_text = example.get("output", "")
                    formatted_example = f"Example {i+1}:\nInput: {input_text}\nOutput: {output_text}"
                else:
                    formatted_example = str(example)
                
                formatted_examples.append(formatted_example)
            except KeyError:
                # Skip examples that can't be formatted with the provided data
                continue
        
        return "\n\n".join(formatted_examples)
    
    def generate_prompt(self, data: Dict[str, Any]) -> str:
        """
        Generate a prompt with examples for few-shot learning.
        
        Args:
            data: Dictionary containing values to be inserted into the template
            
        Returns:
            str: The formatted prompt with examples
        """
        try:
            # Format the main instruction template
            instruction = self.template.format(**data)
            
            # Format the examples
            examples_text = self._format_examples(data)
            
            # Combine instruction with examples
            if examples_text:
                return f"{instruction}\n\nHere are some examples:\n\n{examples_text}\n\nNow complete the task:"
            else:
                return instruction
                
        except KeyError as e:
            raise ValueError(f"Missing required data field: {e}")
        except Exception as e:
            raise ValueError(f"Error generating few-shot prompt: {e}")
