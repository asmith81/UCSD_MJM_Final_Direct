"""
Evaluation configuration implementation.
"""
from typing import Dict, Any, List, Optional, Union
from ..base_config import BaseConfig


class EvaluationConfig(BaseConfig):
    """
    Configuration implementation for evaluation settings.
    Handles nested configuration structures and validates evaluation-specific requirements.
    """

    def __init__(self, data: Dict[str, Any]):
        """
        Initialize with evaluation configuration data.
        
        Args:
            data: Raw configuration data
        """
        self.data = data.get('evaluation', {})
        if not self.data:
            raise ValueError("Configuration must contain an 'evaluation' section")

    def validate(self) -> bool:
        """
        Validate evaluation configuration data structure and values.
        
        Returns:
            bool: True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate required fields
        required_fields = ['metrics', 'dataset', 'output']
        for field in required_fields:
            if field not in self.data:
                raise ValueError(f"Missing required field in evaluation section: {field}")
        
        # Validate metrics
        metrics = self.data['metrics']
        if not isinstance(metrics, list):
            raise ValueError("Metrics must be a list")
        
        # Validate dataset
        dataset = self.data['dataset']
        if not isinstance(dataset, dict):
            raise ValueError("Dataset must be a dictionary")
        if 'path' not in dataset:
            raise ValueError("Dataset must specify a path")
        
        # Validate output
        output = self.data['output']
        if not isinstance(output, dict):
            raise ValueError("Output must be a dictionary")
        if 'format' not in output:
            raise ValueError("Output must specify a format")
        
        return True

    def get_data(self) -> Dict[str, Any]:
        """
        Get the raw evaluation configuration data.
        
        Returns:
            Dict[str, Any]: The evaluation configuration data
        """
        return self.data

    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the configuration using dot notation.
        
        Args:
            key: The key to retrieve (e.g., "metrics", "dataset.path")
            default: Default value if key is not found
            
        Returns:
            Any: The value at the specified key path
        """
        current = self.data
        for part in key.split('.'):
            if not isinstance(current, dict):
                return default
            current = current.get(part, default)
            if current is default:
                return default
        return current

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire section of the configuration.
        
        Args:
            section: The section name (e.g., "metrics", "dataset")
            
        Returns:
            Dict[str, Any]: The section data
        """
        return self.data.get(section, {})

    def get_metrics(self) -> List[str]:
        """
        Get the list of evaluation metrics.
        
        Returns:
            List[str]: List of metric names
        """
        return self.data.get('metrics', [])

    def get_dataset_path(self) -> str:
        """
        Get the dataset path.
        
        Returns:
            str: Path to the dataset
        """
        return self.data.get('dataset', {}).get('path', '')

    def get_output_format(self) -> str:
        """
        Get the output format.
        
        Returns:
            str: Output format (e.g., "json", "csv")
        """
        return self.data.get('output', {}).get('format', '') 