"""Base visualizer interface.

This module defines the base interface for all visualizers in the system.
"""

from abc import ABC, abstractmethod
from pathlib import Path
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
import matplotlib.pyplot as plt


class BaseVisualizer(ABC):
    """Base interface for all visualizers.
    
    This abstract base class defines the standard interface that all visualizers
    must implement, ensuring consistent visualization behavior across the system.
    
    Attributes:
        fig_size: Default figure size (width, height) in inches
        dpi: Default dots per inch for rendered figures
        output_formats: List of output formats to support
    """
    
    def __init__(
        self,
        fig_size: Tuple[int, int] = (10, 6),
        dpi: int = 100,
        output_formats: Optional[List[str]] = None
    ) -> None:
        """Initialize the visualizer.
        
        Args:
            fig_size: Default figure size (width, height) in inches (default: (10, 6))
            dpi: Default dots per inch for rendered figures (default: 100)
            output_formats: Output formats to support (default: ['png', 'pdf'])
        """
        self.fig_size = fig_size
        self.dpi = dpi
        self.output_formats = output_formats or ['png', 'pdf']
        self._logger = logging.getLogger(__name__)
        
    @abstractmethod
    def visualize(self, data: Any) -> plt.Figure:
        """Visualize the provided data.
        
        Args:
            data: The data to visualize
            
        Returns:
            Matplotlib Figure object
        """
        pass
        
    def save(
        self, 
        fig: plt.Figure, 
        filename: Union[str, Path], 
        formats: Optional[List[str]] = None
    ) -> List[Path]:
        """Save the figure to disk in specified formats.
        
        Args:
            fig: Matplotlib Figure to save
            filename: Base filename (without extension)
            formats: List of formats to save as (default: self.output_formats)
            
        Returns:
            List of paths to saved files
        """
        formats = formats or self.output_formats
        saved_files = []
        
        for fmt in formats:
            output_path = Path(f"{filename}.{fmt}")
            try:
                fig.savefig(output_path, format=fmt, dpi=self.dpi, bbox_inches='tight')
                saved_files.append(output_path)
                self._logger.debug(f"Saved figure to {output_path}")
            except Exception as e:
                self._logger.error(f"Failed to save figure as {fmt}: {str(e)}")
                
        return saved_files
        
    def create_figure(self) -> Tuple[plt.Figure, plt.Axes]:
        """Create a new figure with default settings.
        
        Returns:
            Tuple of (Figure, Axes)
        """
        fig, ax = plt.subplots(figsize=self.fig_size, dpi=self.dpi)
        return fig, ax
        
    def configure_default_style(self) -> None:
        """Configure default matplotlib style settings."""
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10
        plt.rcParams['legend.fontsize'] = 10
        plt.rcParams['figure.titlesize'] = 16 