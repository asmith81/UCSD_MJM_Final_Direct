"""Image visualizer implementation.

This module provides visualizations for invoice images and annotations
in the invoice extraction system.
"""

import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from PIL import Image, ImageDraw, ImageFont

from .base_visualizer import BaseVisualizer
from .visualization_utils import plot_image_with_annotations


class ImageVisualizer(BaseVisualizer):
    """Visualizer for invoice images and annotations.
    
    This class provides methods for visualizing invoice images with
    various annotations such as field locations and extraction results.
    
    Attributes:
        fig_size: Figure size (width, height) in inches
        dpi: Dots per inch for rendered figures
        output_formats: Supported output formats
    """
    
    def __init__(
        self,
        fig_size: Tuple[int, int] = (12, 8),
        dpi: int = 150,
        output_formats: Optional[List[str]] = None
    ) -> None:
        """Initialize the image visualizer.
        
        Args:
            fig_size: Figure size (width, height) in inches (default: (12, 8))
            dpi: Dots per inch for rendered figures (default: 150)
            output_formats: Output formats to support (default: ['png', 'pdf'])
        """
        super().__init__(fig_size=fig_size, dpi=dpi, output_formats=output_formats)
        self._logger = logging.getLogger(__name__)
        
    def visualize(self, data: Union[Image.Image, str, Path]) -> plt.Figure:
        """Visualize an invoice image.
        
        Args:
            data: PIL Image or path to image file
            
        Returns:
            Matplotlib Figure with image visualization
        """
        return self.visualize_image(data)
        
    def visualize_image(
        self, 
        image: Union[Image.Image, str, Path],
        title: str = "Invoice Image"
    ) -> plt.Figure:
        """Visualize an invoice image.
        
        Args:
            image: PIL Image or path to image file
            title: Title for the plot (default: "Invoice Image")
            
        Returns:
            Matplotlib Figure with image visualization
        """
        # Load image if it's a path
        if isinstance(image, (str, Path)):
            try:
                img = Image.open(image)
                path_str = str(image)
            except Exception as e:
                self._logger.error(f"Failed to open image {image}: {str(e)}")
                fig, ax = self.create_figure()
                ax.text(0.5, 0.5, f"Error loading image: {str(e)}", 
                       ha='center', va='center', fontsize=12)
                ax.axis('off')
                return fig
        else:
            img = image
            path_str = "image object"
            
        # Create figure
        fig, ax = plt.subplots(figsize=self.fig_size, dpi=self.dpi)
        
        # Display image
        ax.imshow(img)
        ax.set_title(title)
        
        # Add image info as text
        ax.text(
            0.01, 0.01, 
            f"Size: {img.width}x{img.height}, Mode: {img.mode}",
            transform=ax.transAxes,
            fontsize=8,
            verticalalignment='bottom',
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
        )
        
        # Hide axes
        ax.axis('off')
        
        # Make sure layout is compact
        fig.tight_layout()
        
        self._logger.debug(f"Visualized image: {path_str}")
        return fig
    
    def visualize_with_extracted_fields(
        self,
        image: Union[Image.Image, str, Path],
        extracted_fields: Dict[str, Any],
        ground_truth: Optional[Dict[str, Any]] = None,
        title: str = "Extracted Fields"
    ) -> plt.Figure:
        """Visualize an invoice with extracted field values.
        
        Args:
            image: PIL Image or path to image file
            extracted_fields: Dictionary of extracted field values
            ground_truth: Optional dictionary of ground truth values for comparison
            title: Title for the plot (default: "Extracted Fields")
            
        Returns:
            Matplotlib Figure with annotated image
        """
        # Load image if it's a path
        if isinstance(image, (str, Path)):
            try:
                img = Image.open(image)
            except Exception as e:
                self._logger.error(f"Failed to open image {image}: {str(e)}")
                fig, ax = self.create_figure()
                ax.text(0.5, 0.5, f"Error loading image: {str(e)}", 
                       ha='center', va='center', fontsize=12)
                ax.axis('off')
                return fig
        else:
            img = image
            
        # Create figure
        fig, axs = plt.subplots(
            1, 2 if ground_truth else 1,
            figsize=self.fig_size,
            dpi=self.dpi,
            gridspec_kw={'width_ratios': [3, 1] if ground_truth else [1]}
        )
        
        # If only one subplot, convert to array for consistent indexing
        if not ground_truth:
            axs = [axs]
            
        # Display image
        axs[0].imshow(img)
        axs[0].set_title(title)
        axs[0].axis('off')
        
        # Add extracted field values to the image
        y_pos = 0.05
        for field, value in extracted_fields.items():
            # Format the field-value text
            text = f"{field}: {value}"
            
            # Add text with colored background
            axs[0].text(
                0.02, y_pos, 
                text,
                transform=axs[0].transAxes,
                fontsize=10,
                verticalalignment='bottom',
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='blue', pad=3)
            )
            
            y_pos += 0.06  # Move down for next field
            
        # Add comparison if ground truth is provided
        if ground_truth:
            axs[1].axis('off')
            axs[1].set_title("Comparison")
            
            # Create a table for comparison
            table_data = []
            colors = []
            
            for field, gt_value in ground_truth.items():
                extracted_value = extracted_fields.get(field, "")
                
                # Determine if values match (simple string comparison)
                match = str(extracted_value).strip() == str(gt_value).strip()
                row_color = 'lightgreen' if match else 'lightcoral'
                
                table_data.append([field, str(extracted_value), str(gt_value)])
                colors.append([row_color, row_color, row_color])
                
            # Create the table
            table = axs[1].table(
                cellText=table_data,
                colLabels=["Field", "Extracted", "Ground Truth"],
                colWidths=[0.3, 0.35, 0.35],
                loc='center',
                cellColours=colors
            )
            
            # Style the table
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1, 1.5)
            
        fig.tight_layout()
        return fig
        
    def visualize_field_locations(
        self,
        image: Union[Image.Image, str, Path],
        field_locations: Dict[str, Tuple[int, int, int, int]],
        title: str = "Field Locations"
    ) -> plt.Figure:
        """Visualize field locations on an invoice image.
        
        Args:
            image: PIL Image or path to image file
            field_locations: Dictionary mapping field names to (x, y, width, height)
            title: Title for the plot (default: "Field Locations")
            
        Returns:
            Matplotlib Figure with annotated image
        """
        return plot_image_with_annotations(
            image=image,
            annotations=field_locations,
            title=title,
            figsize=self.fig_size,
            box_color='red',
            text_color='black',
            font_size=10
        )
        
    def create_side_by_side_comparison(
        self,
        image: Union[Image.Image, str, Path],
        annotations_list: List[Dict[str, Any]],
        titles: List[str]
    ) -> plt.Figure:
        """Create a side-by-side comparison of multiple annotation sets.
        
        Args:
            image: PIL Image or path to image file
            annotations_list: List of annotation dictionaries
            titles: List of titles for each visualization
            
        Returns:
            Matplotlib Figure with side-by-side comparison
        """
        # Validate inputs
        if len(annotations_list) != len(titles):
            raise ValueError("Number of annotation sets must match number of titles")
            
        if len(annotations_list) == 0:
            raise ValueError("At least one annotation set is required")
            
        # Load image if it's a path
        if isinstance(image, (str, Path)):
            try:
                img = Image.open(image)
            except Exception as e:
                self._logger.error(f"Failed to open image {image}: {str(e)}")
                fig, ax = self.create_figure()
                ax.text(0.5, 0.5, f"Error loading image: {str(e)}", 
                       ha='center', va='center', fontsize=12)
                ax.axis('off')
                return fig
        else:
            img = image
            
        # Create figure with subplots
        n = len(annotations_list)
        fig, axs = plt.subplots(
            1, n,
            figsize=(self.fig_size[0] * n // 2, self.fig_size[1]),
            dpi=self.dpi
        )
        
        # Ensure axs is iterable even for n=1
        if n == 1:
            axs = [axs]
            
        # Create visualizations
        for i, (annotations, title) in enumerate(zip(annotations_list, titles)):
            axs[i].imshow(img)
            axs[i].set_title(title)
            
            # Add annotations
            for field_name, value in annotations.items():
                if isinstance(value, tuple) and len(value) == 4:
                    # Bounding box (x, y, width, height)
                    x, y, width, height = value
                    rect = patches.Rectangle(
                        (x, y), width, height, 
                        linewidth=2, edgecolor='red', facecolor='none', alpha=0.7
                    )
                    axs[i].add_patch(rect)
                    
                    # Add field name label
                    axs[i].text(
                        x, y - 5, field_name, 
                        color='red', fontsize=10, 
                        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
                    )
                elif isinstance(value, str):
                    # Add as text in the corner
                    # Find an empty position
                    y_pos = 0.05 + (i * 0.06) % 0.6
                    axs[i].text(
                        0.02, y_pos, 
                        f"{field_name}: {value}",
                        transform=axs[i].transAxes,
                        fontsize=10,
                        verticalalignment='bottom',
                        bbox=dict(facecolor='white', alpha=0.8, edgecolor='blue', pad=3)
                    )
            
            # Hide axes
            axs[i].axis('off')
            
        fig.tight_layout()
        return fig 