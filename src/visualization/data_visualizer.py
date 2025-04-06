"""Data visualizer implementation.

This module provides visualizations for tabular data and statistics
in the invoice extraction system.
"""

import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Any, Dict, List, Optional, Tuple, Union

from .base_visualizer import BaseVisualizer
from .visualization_utils import create_figure


class DataVisualizer(BaseVisualizer):
    """Visualizer for tabular data and statistics.
    
    This class provides methods for visualizing various aspects
    of tabular data such as distributions, missing values, and correlations.
    
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
        """Initialize the data visualizer.
        
        Args:
            fig_size: Figure size (width, height) in inches (default: (12, 8))
            dpi: Dots per inch for rendered figures (default: 100)
            output_formats: Output formats to support (default: ['png', 'pdf'])
        """
        super().__init__(fig_size=fig_size, dpi=dpi, output_formats=output_formats)
        self._logger = logging.getLogger(__name__)
        
    def visualize(self, data: pd.DataFrame) -> plt.Figure:
        """Visualize a pandas DataFrame.
        
        This is a convenience method that creates a dashboard of
        data visualizations including:
        - Missing value heatmap
        - Numeric column distributions
        - Column type counts
        
        Args:
            data: DataFrame to visualize
            
        Returns:
            Matplotlib Figure with visualizations
        """
        # Create figure with subplots
        fig = plt.figure(figsize=self.fig_size, dpi=self.dpi)
        
        # Create layout grid
        gs = fig.add_gridspec(2, 2)
        
        # Add missing value visualization
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_missing_values(data, ax1)
        
        # Add data type counts
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_dtypes(data, ax2)
        
        # Add numeric distributions 
        ax3 = fig.add_subplot(gs[1, :])
        self._plot_numeric_distributions(data, ax3)
        
        fig.suptitle("Data Overview", fontsize=16)
        fig.tight_layout()
        
        return fig
        
    def plot_missing_values(self, data: pd.DataFrame) -> plt.Figure:
        """Visualize missing values in a DataFrame.
        
        Args:
            data: DataFrame to visualize
            
        Returns:
            Matplotlib Figure with missing values visualization
        """
        fig, ax = self.create_figure()
        self._plot_missing_values(data, ax)
        fig.tight_layout()
        return fig
        
    def _plot_missing_values(self, data: pd.DataFrame, ax: plt.Axes) -> None:
        """Plot missing values on the given axes.
        
        Args:
            data: DataFrame to visualize
            ax: Matplotlib Axes to plot on
        """
        # Calculate missing values by column
        missing = data.isnull().sum().sort_values(ascending=False)
        missing_pct = (missing / len(data) * 100).round(2)
        
        # Filter to only show columns with missing values
        missing = missing[missing > 0]
        missing_pct = missing_pct[missing_pct > 0]
        
        if len(missing) == 0:
            ax.text(0.5, 0.5, "No missing values", 
                   ha='center', va='center', fontsize=12)
            ax.set_title("Missing Values")
            ax.axis('off')
            return
            
        # Create DataFrame for plotting
        missing_df = pd.DataFrame({
            'Count': missing,
            'Percent': missing_pct
        })
        
        # Plot as horizontal bars
        missing_df['Percent'].sort_values().plot(
            kind='barh',
            color='#3498db',
            ax=ax
        )
        
        # Add percentage labels
        for i, (idx, row) in enumerate(missing_df.iterrows()):
            ax.text(
                row['Percent'] + 0.5, 
                i, 
                f"{row['Percent']}% ({row['Count']})",
                va='center'
            )
            
        ax.set_title("Missing Values by Column")
        ax.set_xlabel("Percentage of Missing Values")
        ax.set_xlim(0, max(missing_pct) * 1.1)
        
    def plot_distributions(self, data: pd.DataFrame, columns: Optional[List[str]] = None) -> plt.Figure:
        """Visualize distributions of numeric columns.
        
        Args:
            data: DataFrame to visualize
            columns: List of columns to include (default: all numeric columns)
            
        Returns:
            Matplotlib Figure with distribution plots
        """
        fig, ax = self.create_figure()
        self._plot_numeric_distributions(data, ax, columns)
        fig.tight_layout()
        return fig
        
    def _plot_numeric_distributions(
        self, 
        data: pd.DataFrame, 
        ax: plt.Axes,
        columns: Optional[List[str]] = None
    ) -> None:
        """Plot numeric distributions on the given axes.
        
        Args:
            data: DataFrame to visualize
            ax: Matplotlib Axes to plot on
            columns: List of columns to include (default: all numeric columns)
        """
        # Filter to numeric columns
        numeric_cols = columns or data.select_dtypes(include=['number']).columns.tolist()
        
        if not numeric_cols:
            ax.text(0.5, 0.5, "No numeric columns to display", 
                   ha='center', va='center', fontsize=12)
            ax.set_title("Numeric Distributions")
            ax.axis('off')
            return
            
        if len(numeric_cols) > 6:
            numeric_cols = numeric_cols[:6]
            self._logger.warning(f"Too many numeric columns. Showing only first 6.")
            
        # Create distribution plots
        plot_data = data[numeric_cols].melt(var_name='Column', value_name='Value')
        sns.violinplot(
            x='Column', 
            y='Value', 
            data=plot_data,
            ax=ax,
            palette='Set3'
        )
        
        ax.set_title("Distributions of Numeric Columns")
        
    def plot_dtypes(self, data: pd.DataFrame) -> plt.Figure:
        """Visualize data types in the DataFrame.
        
        Args:
            data: DataFrame to visualize
            
        Returns:
            Matplotlib Figure with data type visualization
        """
        fig, ax = self.create_figure()
        self._plot_dtypes(data, ax)
        fig.tight_layout()
        return fig
        
    def _plot_dtypes(self, data: pd.DataFrame, ax: plt.Axes) -> None:
        """Plot data types on the given axes.
        
        Args:
            data: DataFrame to visualize
            ax: Matplotlib Axes to plot on
        """
        # Get counts of each data type
        dtype_counts = pd.Series(data.dtypes).value_counts()
        
        # Convert dtype objects to strings for consistent display
        dtype_counts.index = [str(dtype) for dtype in dtype_counts.index]
        
        # Create pie chart
        ax.pie(
            dtype_counts,
            labels=dtype_counts.index,
            autopct='%1.1f%%',
            startangle=90,
            colors=sns.color_palette('Set3', len(dtype_counts))
        )
        
        ax.set_title(f"Data Types (Total Columns: {len(data.columns)})")
        
    def plot_correlations(self, data: pd.DataFrame, method: str = 'pearson') -> plt.Figure:
        """Visualize correlations between numeric columns.
        
        Args:
            data: DataFrame to visualize
            method: Correlation method ('pearson', 'kendall', 'spearman')
            
        Returns:
            Matplotlib Figure with correlation heatmap
        """
        # Filter to numeric columns
        numeric_data = data.select_dtypes(include=['number'])
        
        if numeric_data.shape[1] < 2:
            fig, ax = self.create_figure()
            ax.text(0.5, 0.5, "Need at least 2 numeric columns for correlation", 
                   ha='center', va='center', fontsize=12)
            ax.set_title("Correlation Matrix")
            ax.axis('off')
            return fig
            
        # Calculate correlation matrix
        corr = numeric_data.corr(method=method)
        
        # Create figure (adjust size based on number of columns)
        n_cols = len(corr.columns)
        figsize = (max(8, n_cols * 0.8), max(6, n_cols * 0.7))
        fig, ax = plt.subplots(figsize=figsize, dpi=self.dpi)
        
        # Create heatmap
        mask = np.triu(np.ones_like(corr, dtype=bool))
        cmap = sns.diverging_palette(230, 20, as_cmap=True)
        
        sns.heatmap(
            corr,
            mask=mask,
            cmap=cmap,
            vmax=1,
            vmin=-1,
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8},
            annot=True,
            fmt=".2f",
            ax=ax
        )
        
        ax.set_title(f"Correlation Matrix ({method.capitalize()})")
        fig.tight_layout()
        
        return fig 