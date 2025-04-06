"""Results visualizer implementation.

This module provides visualizations for evaluation results and comparisons
in the invoice extraction system.
"""

import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Any, Dict, List, Optional, Tuple, Union

from .base_visualizer import BaseVisualizer
from .visualization_utils import plot_field_accuracy_bars


class ResultsVisualizer(BaseVisualizer):
    """Visualizer for evaluation results and comparisons.
    
    This class provides methods for visualizing results from
    model evaluation and comparing different models and prompts.
    
    Attributes:
        fig_size: Figure size (width, height) in inches
        dpi: Dots per inch for rendered figures
        output_formats: Supported output formats
    """
    
    def __init__(
        self,
        fig_size: Tuple[int, int] = (12, 8),
        dpi: int = 100,
        output_formats: Optional[List[str]] = None
    ) -> None:
        """Initialize the results visualizer.
        
        Args:
            fig_size: Figure size (width, height) in inches (default: (12, 8))
            dpi: Dots per inch for rendered figures (default: 100)
            output_formats: Output formats to support (default: ['png', 'pdf'])
        """
        super().__init__(fig_size=fig_size, dpi=dpi, output_formats=output_formats)
        self._logger = logging.getLogger(__name__)
        
    def visualize(self, data: Dict[str, Any]) -> plt.Figure:
        """Visualize evaluation results.
        
        Args:
            data: Dictionary containing evaluation results
            
        Returns:
            Matplotlib Figure with results visualization
        """
        # Check if data has field-level results
        if "field_results" in data:
            return self.visualize_field_results(data["field_results"])
        else:
            return self.visualize_summary_results(data)
            
    def visualize_field_results(
        self,
        field_results: Dict[str, Dict[str, Any]],
        title: str = "Field Extraction Results"
    ) -> plt.Figure:
        """Visualize field-level extraction results.
        
        Args:
            field_results: Dictionary mapping field names to result dictionaries
            title: Title for the plot (default: "Field Extraction Results")
            
        Returns:
            Matplotlib Figure with field results visualization
        """
        # Extract field accuracy data
        accuracy_data = {}
        for field, result in field_results.items():
            # Skip fields missing in either ground truth or extracted
            if result.get("missing_in_ground_truth") or result.get("missing_in_extracted"):
                continue
                
            # Use normalized match if available, otherwise use exact match
            accuracy_data[field] = 1.0 if result.get("normalized_match", False) else 0.0
            
        # Use the utility function to create the visualization
        fig = plot_field_accuracy_bars(
            accuracy_data=accuracy_data,
            title=title,
            color="#3498db",
            threshold=0.8
        )
        
        return fig
        
    def visualize_summary_results(
        self,
        summary_data: Dict[str, Any],
        title: str = "Extraction Results Summary"
    ) -> plt.Figure:
        """Visualize summary extraction results.
        
        Args:
            summary_data: Dictionary containing summary statistics
            title: Title for the plot (default: "Extraction Results Summary")
            
        Returns:
            Matplotlib Figure with summary visualization
        """
        # Create figure
        fig, ax = self.create_figure()
        
        # Extract relevant metrics
        metrics = [
            ("Exact Match Rate", summary_data.get("exact_match_rate", 0)),
            ("Normalized Match Rate", summary_data.get("normalized_match_rate", 0)),
            ("Common Field Match Rate", summary_data.get("common_field_match_rate", 0))
        ]
        
        # Create bar chart
        names, values = zip(*metrics)
        bars = ax.bar(names, values, color=["#3498db", "#2ecc71", "#e74c3c"])
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f"{height:.2f}",
                   ha='center', va='bottom', fontsize=10)
                   
        # Add a threshold line at 0.8
        ax.axhline(y=0.8, color='r', linestyle='--', alpha=0.7, 
                  label='Threshold (80%)')
        
        # Customize the chart
        ax.set_ylim(0, 1.1)
        ax.set_ylabel("Rate")
        ax.set_title(title)
        ax.legend()
        
        # Add additional info as text
        info_text = (
            f"Total Fields: {summary_data.get('total_fields_count', 0)}\n"
            f"Common Fields: {summary_data.get('common_fields_count', 0)}\n"
            f"Missing in Extracted: {len(summary_data.get('missing_in_extracted', []))}\n"
            f"Missing in Ground Truth: {len(summary_data.get('missing_in_ground_truth', []))}"
        )
        
        ax.text(
            0.02, 0.02, 
            info_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='bottom',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray', pad=5)
        )
        
        fig.tight_layout()
        return fig
        
    def visualize_model_comparison(
        self,
        model_results: Dict[str, Dict[str, float]],
        metric: str = "normalized_match_rate",
        title: str = "Model Comparison"
    ) -> plt.Figure:
        """Visualize comparison between different models.
        
        Args:
            model_results: Dictionary mapping model names to result dictionaries
            metric: Metric to compare (default: "normalized_match_rate")
            title: Title for the plot (default: "Model Comparison")
            
        Returns:
            Matplotlib Figure with model comparison
        """
        # Extract the specified metric for each model
        models = list(model_results.keys())
        values = [results.get(metric, 0) for results in model_results.values()]
        
        # Sort by performance
        sorted_indices = np.argsort(values)[::-1]  # Descending order
        models = [models[i] for i in sorted_indices]
        values = [values[i] for i in sorted_indices]
        
        # Create bar chart
        fig, ax = self.create_figure()
        bars = ax.bar(models, values, color=sns.color_palette("muted", len(models)))
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f"{height:.2f}",
                   ha='center', va='bottom', fontsize=10)
                   
        # Add a threshold line at 0.8
        ax.axhline(y=0.8, color='r', linestyle='--', alpha=0.7, 
                  label='Threshold (80%)')
        
        # Customize the chart
        ax.set_ylim(0, 1.1)
        ax.set_ylabel(metric.replace("_", " ").title())
        ax.set_title(title)
        ax.legend()
        
        # Format x-axis labels if they're too long
        if max(len(model) for model in models) > 10:
            plt.xticks(rotation=45, ha='right')
            
        fig.tight_layout()
        return fig
        
    def visualize_prompt_comparison(
        self,
        prompt_results: Dict[str, Dict[str, float]],
        metric: str = "normalized_match_rate",
        title: str = "Prompt Comparison"
    ) -> plt.Figure:
        """Visualize comparison between different prompt strategies.
        
        Args:
            prompt_results: Dictionary mapping prompt names to result dictionaries
            metric: Metric to compare (default: "normalized_match_rate")
            title: Title for the plot (default: "Prompt Comparison")
            
        Returns:
            Matplotlib Figure with prompt comparison
        """
        # This is essentially the same as model_comparison but with prompt-specific title
        return self.visualize_model_comparison(
            model_results=prompt_results,
            metric=metric,
            title=title
        )
        
    def visualize_model_prompt_heatmap(
        self,
        results_matrix: Dict[str, Dict[str, float]],
        metric: str = "normalized_match_rate",
        title: str = "Model-Prompt Performance Matrix"
    ) -> plt.Figure:
        """Visualize performance matrix of models and prompts.
        
        Args:
            results_matrix: Dictionary mapping model-prompt combos to result values
                Format: {model_name: {prompt_name: value}}
            metric: Metric to compare (default: "normalized_match_rate")
            title: Title for the plot (default: "Model-Prompt Performance Matrix")
            
        Returns:
            Matplotlib Figure with heatmap visualization
        """
        # Extract model and prompt names
        models = list(results_matrix.keys())
        prompts = set()
        for model_results in results_matrix.values():
            prompts.update(model_results.keys())
        prompts = sorted(list(prompts))
        
        # Create data matrix
        data = np.zeros((len(models), len(prompts)))
        for i, model in enumerate(models):
            for j, prompt in enumerate(prompts):
                data[i, j] = results_matrix[model].get(prompt, 0)
                
        # Create heatmap
        fig, ax = plt.subplots(figsize=self.fig_size, dpi=self.dpi)
        sns.heatmap(
            data,
            annot=True,
            fmt=".2f",
            cmap="YlGnBu",
            xticklabels=prompts,
            yticklabels=models,
            ax=ax
        )
        
        # Customize the chart
        ax.set_title(title)
        ax.set_xlabel("Prompt Strategy")
        ax.set_ylabel("Model")
        
        # Format labels if they're too long
        if max(len(model) for model in models) > 10:
            plt.yticks(rotation=0)
            
        if max(len(prompt) for prompt in prompts) > 10:
            plt.xticks(rotation=45, ha='right')
            
        fig.tight_layout()
        return fig 