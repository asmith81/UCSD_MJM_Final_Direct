"""Visualization service implementation.

This module provides a service for coordinating visualization tasks
across different types of data in the invoice extraction system.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

from .base_visualizer import BaseVisualizer
from .data_visualizer import DataVisualizer
from .image_visualizer import ImageVisualizer
from .results_visualizer import ResultsVisualizer
from .visualization_utils import configure_matplotlib_defaults


class VisualizationService:
    """Service for coordinating visualization tasks.
    
    This service provides a unified interface for creating visualizations
    across different data types, handling the appropriate visualizer selection
    and configuration.
    
    Attributes:
        data_visualizer: Visualizer for tabular data
        image_visualizer: Visualizer for invoice images
        results_visualizer: Visualizer for evaluation results
        output_dir: Directory for saving visualizations
    """
    
    def __init__(
        self,
        output_dir: Optional[Union[str, Path]] = None,
        data_visualizer: Optional[DataVisualizer] = None,
        image_visualizer: Optional[ImageVisualizer] = None,
        results_visualizer: Optional[ResultsVisualizer] = None
    ) -> None:
        """Initialize the visualization service.
        
        Args:
            output_dir: Directory for saving visualizations (default: ./results/visualizations)
            data_visualizer: DataVisualizer instance (default: create new instance)
            image_visualizer: ImageVisualizer instance (default: create new instance)
            results_visualizer: ResultsVisualizer instance (default: create new instance)
        """
        # Set up output directory
        self.output_dir = Path(output_dir) if output_dir else Path("./results/visualizations")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up visualizers (with dependency injection)
        self.data_visualizer = data_visualizer or DataVisualizer()
        self.image_visualizer = image_visualizer or ImageVisualizer()
        self.results_visualizer = results_visualizer or ResultsVisualizer()
        
        # Set up logging
        self._logger = logging.getLogger(__name__)
        
        # Configure default matplotlib settings
        configure_matplotlib_defaults()
        
    def visualize_and_save(
        self,
        data: Any,
        visualizer: BaseVisualizer,
        filename: str,
        subdirectory: Optional[str] = None,
        formats: Optional[List[str]] = None
    ) -> List[Path]:
        """Visualize data and save to disk.
        
        Args:
            data: Data to visualize
            visualizer: Visualizer to use
            filename: Base filename (without extension)
            subdirectory: Optional subdirectory within output_dir
            formats: Output formats (default: from visualizer)
            
        Returns:
            List of saved file paths
        """
        # Create figure using visualizer
        fig = visualizer.visualize(data)
        
        # Determine output path
        output_path = self.output_dir
        if subdirectory:
            output_path = output_path / subdirectory
            output_path.mkdir(parents=True, exist_ok=True)
            
        full_path = output_path / filename
        
        # Save figure
        saved_files = visualizer.save(fig, full_path, formats)
        
        # Close figure to free memory
        plt.close(fig)
        
        self._logger.info(f"Saved visualization to {full_path}")
        return saved_files
        
    def visualize_ground_truth(
        self,
        ground_truth_data: pd.DataFrame,
        filename: str = "ground_truth_overview",
        subdirectory: str = "data",
        formats: Optional[List[str]] = None
    ) -> List[Path]:
        """Visualize ground truth data.
        
        Args:
            ground_truth_data: DataFrame with ground truth data
            filename: Base filename (default: "ground_truth_overview")
            subdirectory: Output subdirectory (default: "data")
            formats: Output formats (default: from visualizer)
            
        Returns:
            List of saved file paths
        """
        return self.visualize_and_save(
            data=ground_truth_data,
            visualizer=self.data_visualizer,
            filename=filename,
            subdirectory=subdirectory,
            formats=formats
        )
        
    def visualize_invoice_image(
        self,
        image: Union[Image.Image, str, Path],
        filename: Optional[str] = None,
        subdirectory: str = "images",
        formats: Optional[List[str]] = None
    ) -> List[Path]:
        """Visualize an invoice image.
        
        Args:
            image: PIL Image or path to image file
            filename: Base filename (default: derived from image path)
            subdirectory: Output subdirectory (default: "images")
            formats: Output formats (default: from visualizer)
            
        Returns:
            List of saved file paths
        """
        # Derive filename from image path if not provided
        if filename is None:
            if isinstance(image, (str, Path)):
                filename = Path(image).stem
            else:
                filename = "invoice_image"
                
        return self.visualize_and_save(
            data=image,
            visualizer=self.image_visualizer,
            filename=filename,
            subdirectory=subdirectory,
            formats=formats
        )
        
    def visualize_extraction_results(
        self,
        image: Union[Image.Image, str, Path],
        extracted_fields: Dict[str, Any],
        ground_truth: Optional[Dict[str, Any]] = None,
        filename: Optional[str] = None,
        subdirectory: str = "results",
        formats: Optional[List[str]] = None
    ) -> List[Path]:
        """Visualize extraction results for an invoice.
        
        Args:
            image: PIL Image or path to image file
            extracted_fields: Dictionary of extracted field values
            ground_truth: Optional dictionary of ground truth values for comparison
            filename: Base filename (default: derived from image path)
            subdirectory: Output subdirectory (default: "results")
            formats: Output formats (default: from visualizer)
            
        Returns:
            List of saved file paths
        """
        # Derive filename from image path if not provided
        if filename is None:
            if isinstance(image, (str, Path)):
                filename = f"{Path(image).stem}_extraction"
            else:
                filename = "extraction_results"
                
        # Create custom visualization
        fig = self.image_visualizer.visualize_with_extracted_fields(
            image=image,
            extracted_fields=extracted_fields,
            ground_truth=ground_truth
        )
        
        # Determine output path
        output_path = self.output_dir
        if subdirectory:
            output_path = output_path / subdirectory
            output_path.mkdir(parents=True, exist_ok=True)
            
        full_path = output_path / filename
        
        # Save figure
        saved_files = self.image_visualizer.save(fig, full_path, formats)
        
        # Close figure to free memory
        plt.close(fig)
        
        self._logger.info(f"Saved extraction visualization to {full_path}")
        return saved_files
        
    def visualize_model_comparison(
        self,
        model_results: Dict[str, Dict[str, float]],
        metric: str = "normalized_match_rate",
        filename: str = "model_comparison",
        subdirectory: str = "comparisons",
        formats: Optional[List[str]] = None
    ) -> List[Path]:
        """Visualize a comparison between different models.
        
        Args:
            model_results: Dictionary mapping model names to result dictionaries
            metric: Metric to compare (default: "normalized_match_rate")
            filename: Base filename (default: "model_comparison")
            subdirectory: Output subdirectory (default: "comparisons")
            formats: Output formats (default: from visualizer)
            
        Returns:
            List of saved file paths
        """
        # Create visualization
        fig = self.results_visualizer.visualize_model_comparison(
            model_results=model_results,
            metric=metric,
            title=f"Model Comparison - {metric.replace('_', ' ').title()}"
        )
        
        # Determine output path
        output_path = self.output_dir
        if subdirectory:
            output_path = output_path / subdirectory
            output_path.mkdir(parents=True, exist_ok=True)
            
        full_path = output_path / filename
        
        # Save figure
        saved_files = self.results_visualizer.save(fig, full_path, formats)
        
        # Close figure to free memory
        plt.close(fig)
        
        self._logger.info(f"Saved model comparison to {full_path}")
        return saved_files
        
    def generate_summary_dashboard(
        self,
        ground_truth_data: pd.DataFrame,
        model_results: Dict[str, Dict[str, float]],
        sample_image: Union[Image.Image, str, Path],
        sample_extraction: Dict[str, Any],
        filename: str = "dashboard",
        subdirectory: str = "",
        formats: Optional[List[str]] = None
    ) -> List[Path]:
        """Generate a comprehensive dashboard with multiple visualizations.
        
        Args:
            ground_truth_data: DataFrame with ground truth data
            model_results: Dictionary mapping model names to result dictionaries
            sample_image: Sample invoice image
            sample_extraction: Sample extraction results
            filename: Base filename (default: "dashboard")
            subdirectory: Output subdirectory (default: "")
            formats: Output formats (default: from visualizer)
            
        Returns:
            List of saved file paths
        """
        # Create a multi-panel figure
        fig = plt.figure(figsize=(20, 16), dpi=150)
        
        # Create layout grid
        gs = fig.add_gridspec(2, 2)
        
        # Panel 1: Data overview
        ax1 = fig.add_subplot(gs[0, 0])
        self.data_visualizer._plot_missing_values(ground_truth_data, ax1)
        
        # Panel 2: Model comparison
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_model_comparison(model_results, ax2)
        
        # Panel 3: Sample image with extraction
        ax3 = fig.add_subplot(gs[1, :])
        self._plot_sample_extraction(sample_image, sample_extraction, ax3)
        
        # Add title
        fig.suptitle("Invoice Extraction Dashboard", fontsize=20)
        fig.tight_layout()
        
        # Determine output path
        output_path = self.output_dir
        if subdirectory:
            output_path = output_path / subdirectory
            output_path.mkdir(parents=True, exist_ok=True)
            
        full_path = output_path / filename
        
        # Save figure
        formats = formats or ['png', 'pdf']
        saved_files = []
        
        for fmt in formats:
            output_file = f"{full_path}.{fmt}"
            fig.savefig(output_file, format=fmt, dpi=150, bbox_inches='tight')
            saved_files.append(Path(output_file))
            
        # Close figure to free memory
        plt.close(fig)
        
        self._logger.info(f"Saved dashboard to {full_path}")
        return saved_files
        
    def _plot_model_comparison(
        self,
        model_results: Dict[str, Dict[str, float]],
        ax: plt.Axes,
        metric: str = "normalized_match_rate"
    ) -> None:
        """Helper method to plot model comparison on given axes.
        
        Args:
            model_results: Dictionary mapping model names to result dictionaries
            ax: Matplotlib axes to plot on
            metric: Metric to compare (default: "normalized_match_rate")
        """
        # Extract the specified metric for each model
        models = list(model_results.keys())
        values = [results.get(metric, 0) for results in model_results.values()]
        
        # Sort by performance
        sorted_indices = np.argsort(values)[::-1]  # Descending order
        models = [models[i] for i in sorted_indices]
        values = [values[i] for i in sorted_indices]
        
        # Create bar chart
        bars = ax.bar(models, values, color=['#3498db', '#2ecc71', '#e74c3c'])
        
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
        ax.set_title("Model Comparison")
        
        # Format x-axis labels if they're too long
        if max(len(model) for model in models) > 10:
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
    def _plot_sample_extraction(
        self,
        image: Union[Image.Image, str, Path],
        extraction: Dict[str, Any],
        ax: plt.Axes
    ) -> None:
        """Helper method to plot sample extraction on given axes.
        
        Args:
            image: PIL Image or path to image file
            extraction: Dictionary of extracted field values
            ax: Matplotlib axes to plot on
        """
        # Load image if it's a path
        if isinstance(image, (str, Path)):
            try:
                img = Image.open(image)
            except Exception as e:
                self._logger.error(f"Failed to open image {image}: {str(e)}")
                ax.text(0.5, 0.5, f"Error loading image: {str(e)}", 
                      ha='center', va='center', fontsize=12)
                ax.axis('off')
                return
        else:
            img = image
            
        # Display image
        ax.imshow(img)
        ax.set_title("Sample Extraction")
        
        # Add extracted field values to the image
        y_pos = 0.05
        for field, value in extraction.items():
            # Format the field-value text
            text = f"{field}: {value}"
            
            # Add text with colored background
            ax.text(
                0.02, y_pos, 
                text,
                transform=ax.transAxes,
                fontsize=10,
                verticalalignment='bottom',
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='blue', pad=3)
            )
            
            y_pos += 0.06  # Move down for next field
            
        # Hide axes
        ax.axis('off')
