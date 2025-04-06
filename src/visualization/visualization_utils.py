"""Visualization utility functions.

This module provides utility functions for visualizing data in the invoice extraction system.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from PIL import Image


def configure_matplotlib_defaults() -> None:
    """Configure default matplotlib style settings for consistent visualizations."""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['figure.titlesize'] = 16


def create_figure(
    figsize: Tuple[int, int] = (10, 6),
    dpi: int = 100,
    style: str = 'seaborn-v0_8-whitegrid'
) -> Tuple[plt.Figure, plt.Axes]:
    """Create a new figure with specified settings.
    
    Args:
        figsize: Figure size in inches (width, height) (default: (10, 6))
        dpi: Dots per inch (default: 100)
        style: Matplotlib style to use (default: 'seaborn-v0_8-whitegrid')
        
    Returns:
        Tuple of (Figure, Axes)
    """
    plt.style.use(style)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    return fig, ax


def save_figure(
    fig: plt.Figure,
    filename: Union[str, Path],
    formats: Optional[List[str]] = None,
    dpi: int = 100
) -> List[Path]:
    """Save a figure to disk in specified formats.
    
    Args:
        fig: Matplotlib Figure to save
        filename: Base filename (without extension)
        formats: List of formats to save as (default: ['png', 'pdf'])
        dpi: Dots per inch (default: 100)
        
    Returns:
        List of paths to saved files
    """
    formats = formats or ['png', 'pdf']
    saved_files = []
    
    for fmt in formats:
        output_path = Path(f"{filename}.{fmt}")
        try:
            fig.savefig(output_path, format=fmt, dpi=dpi, bbox_inches='tight')
            saved_files.append(output_path)
        except Exception as e:
            print(f"Failed to save figure as {fmt}: {str(e)}")
            
    return saved_files


def plot_confusion_matrix(
    confusion_matrix: np.ndarray,
    class_names: Optional[List[str]] = None,
    title: str = 'Confusion Matrix',
    cmap: str = 'Blues',
    normalize: bool = True
) -> plt.Figure:
    """Plot a confusion matrix.
    
    Args:
        confusion_matrix: 2D numpy array with confusion matrix data
        class_names: List of class names (default: None)
        title: Title for the plot (default: 'Confusion Matrix')
        cmap: Colormap to use (default: 'Blues')
        normalize: Whether to normalize the confusion matrix (default: True)
        
    Returns:
        Matplotlib Figure with confusion matrix visualization
    """
    if normalize:
        confusion_matrix = confusion_matrix.astype('float') / confusion_matrix.sum(axis=1)[:, np.newaxis]
        
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        confusion_matrix,
        annot=True,
        fmt='.2f' if normalize else 'd',
        cmap=cmap,
        cbar=True,
        square=True,
        xticklabels=class_names,
        yticklabels=class_names,
        ax=ax
    )
    
    ax.set_ylabel('True')
    ax.set_xlabel('Predicted')
    ax.set_title(title)
    
    fig.tight_layout()
    return fig


def plot_field_accuracy_bars(
    accuracy_data: Dict[str, float],
    title: str = 'Field Extraction Accuracy',
    color: str = '#3498db',
    threshold: Optional[float] = 0.8
) -> plt.Figure:
    """Plot bar chart of field extraction accuracy.
    
    Args:
        accuracy_data: Dictionary mapping field names to accuracy values (0-1)
        title: Title for the plot (default: 'Field Extraction Accuracy')
        color: Bar color (default: '#3498db')
        threshold: Optional threshold to highlight (default: 0.8)
        
    Returns:
        Matplotlib Figure with bar chart
    """
    fields = list(accuracy_data.keys())
    values = list(accuracy_data.values())
    
    # Sort by accuracy value
    sorted_indices = np.argsort(values)
    fields = [fields[i] for i in sorted_indices]
    values = [values[i] for i in sorted_indices]
    
    fig, ax = plt.subplots(figsize=(10, max(6, len(fields) * 0.4)))
    
    bars = ax.barh(fields, values, color=color, alpha=0.7)
    
    # Add a threshold line if specified
    if threshold is not None:
        ax.axvline(x=threshold, color='red', linestyle='--', alpha=0.7, 
                  label=f'Threshold ({threshold:.0%})')
        ax.legend()
    
    # Add values at the end of each bar
    for i, v in enumerate(values):
        ax.text(v + 0.01, i, f'{v:.1%}', va='center')
    
    # Labels and title
    ax.set_xlabel('Accuracy')
    ax.set_title(title)
    ax.set_xlim(0, 1.1)
    
    fig.tight_layout()
    return fig


def plot_image_with_annotations(
    image: Union[str, Path, Image.Image, np.ndarray],
    annotations: Dict[str, Union[Tuple[int, int, int, int], List[Tuple[int, int]]]],
    title: str = 'Annotated Image',
    figsize: Tuple[int, int] = (12, 8),
    box_color: str = 'red',
    text_color: str = 'white',
    font_size: int = 10
) -> plt.Figure:
    """Plot an image with box annotations.
    
    Args:
        image: PIL Image, numpy array, or path to image file
        annotations: Dictionary mapping field names to bounding boxes (x, y, width, height) 
                    or point coordinates [(x1, y1), (x2, y2),...]
        title: Title for the plot (default: 'Annotated Image')
        figsize: Figure size (width, height) (default: (12, 8))
        box_color: Color for bounding boxes (default: 'red')
        text_color: Color for annotation text (default: 'white')
        font_size: Size of annotation text (default: 10)
        
    Returns:
        Matplotlib Figure with annotated image
    """
    # Load image if it's a path
    if isinstance(image, (str, Path)):
        img = Image.open(image)
    elif isinstance(image, np.ndarray):
        img = Image.fromarray(image)
    elif isinstance(image, Image.Image):
        img = image
    else:
        raise ValueError("Image must be a PIL Image, numpy array, or path to image file")
    
    # Create figure and display image
    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(img)
    ax.set_title(title)
    
    # Add annotations
    for field_name, coords in annotations.items():
        if isinstance(coords, tuple) and len(coords) == 4:
            # Bounding box (x, y, width, height)
            x, y, width, height = coords
            rect = patches.Rectangle(
                (x, y), width, height, 
                linewidth=2, edgecolor=box_color, facecolor='none', alpha=0.7
            )
            ax.add_patch(rect)
            
            # Add field name label
            ax.text(
                x, y - 5, field_name, 
                color=box_color, fontsize=font_size, 
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
            )
            
        elif isinstance(coords, list) and all(isinstance(p, tuple) and len(p) == 2 for p in coords):
            # Polygon or points [(x1, y1), (x2, y2), ...]
            points = np.array(coords)
            ax.plot(points[:, 0], points[:, 1], 'o-', color=box_color, linewidth=2, alpha=0.7)
            
            # Add field name label at the first point
            if len(coords) > 0:
                ax.text(
                    coords[0][0], coords[0][1] - 5, field_name, 
                    color=box_color, fontsize=font_size, 
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
                )
    
    # Hide axes
    ax.axis('off')
    fig.tight_layout()
    return fig 