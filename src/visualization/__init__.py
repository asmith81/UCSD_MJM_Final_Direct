"""Visualization components.

This package provides visualizations for data, images, and results
in the invoice extraction system.
"""

from .base_visualizer import BaseVisualizer
from .data_visualizer import DataVisualizer
from .image_visualizer import ImageVisualizer
from .results_visualizer import ResultsVisualizer
from .visualization_utils import (
    save_figure,
    configure_matplotlib_defaults,
    create_figure,
    plot_confusion_matrix,
    plot_field_accuracy_bars,
    plot_image_with_annotations
)

__all__ = [
    'BaseVisualizer',
    'DataVisualizer',
    'ImageVisualizer',
    'ResultsVisualizer',
    'save_figure',
    'configure_matplotlib_defaults',
    'create_figure',
    'plot_confusion_matrix',
    'plot_field_accuracy_bars',
    'plot_image_with_annotations'
]
