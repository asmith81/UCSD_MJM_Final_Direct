"""
Service for evaluating model performance.
"""
from typing import Dict, Any, List
from pathlib import Path

from .metrics_calculator import MetricsCalculator
from .results_manager import ResultsManager
from ..config import ConfigType

class EvaluationService:
    """
    Service for evaluating model performance and managing results.
    Uses configuration management for evaluation settings.
    """

    def __init__(self, metrics_calculator: MetricsCalculator, results_manager: ResultsManager, config_manager):
        """
        Initialize the evaluation service.

        Args:
            metrics_calculator: Calculator for computing evaluation metrics
            results_manager: Manager for storing and retrieving results
            config_manager: Configuration manager instance
            
        Raises:
            ValueError: If any dependency is None
        """
        if metrics_calculator is None or results_manager is None or config_manager is None:
            raise ValueError("All dependencies (metrics_calculator, results_manager, config_manager) are required")
            
        self.metrics_calculator = metrics_calculator
        self.results_manager = results_manager
        self._config_manager = config_manager
        self._load_config()

    def _load_config(self):
        """Load evaluation configuration."""
        self.config = self._config_manager.get_config(ConfigType.EVALUATION)
        
        # Set up evaluation parameters from config
        self.metrics = self.config.get_metrics()
        self.dataset_path = Path(self.config.get_dataset_path())
        self.output_format = self.config.get_output_format()

    def evaluate_model(self, model_name: str, predictions: Dict[str, Any]) -> Dict[str, float]:
        """
        Evaluate model performance against ground truth.

        Args:
            model_name: Name of the model being evaluated
            predictions: Model predictions to evaluate

        Returns:
            Dict[str, float]: Computed metrics
        """
        # Load ground truth data
        ground_truth = self.results_manager.load_ground_truth(self.dataset_path)

        # Calculate metrics
        results = {}
        for metric in self.metrics:
            score = self.metrics_calculator.calculate_metric(
                metric, predictions, ground_truth
            )
            results[metric] = score

        # Store results
        self.results_manager.save_results(
            model_name, results, format=self.output_format
        )

        return results

    def get_model_performance(self, model_name: str) -> Dict[str, float]:
        """
        Get stored performance metrics for a model.

        Args:
            model_name: Name of the model

        Returns:
            Dict[str, float]: Stored metrics for the model
        """
        return self.results_manager.load_results(model_name)

    def compare_models(self, model_names: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Compare performance metrics across multiple models.

        Args:
            model_names: List of model names to compare

        Returns:
            Dict[str, Dict[str, float]]: Metrics for each model
        """
        results = {}
        for model_name in model_names:
            results[model_name] = self.get_model_performance(model_name)
        return results
