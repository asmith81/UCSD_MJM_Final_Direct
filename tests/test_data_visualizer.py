import os
import tempfile
import pytest
import pandas as pd
import matplotlib
# Set non-interactive backend for testing
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

from src.visualization.data_visualizer import DataVisualizer


class TestDataVisualizer:
    """Test suite for the DataVisualizer class."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for output files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Clean up
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_dataframe(self):
        """Create a sample DataFrame for testing."""
        return pd.DataFrame({
            'numeric_col1': [1, 2, 3, 4, 5, None, 7, 8, 9, 10],
            'numeric_col2': [10.5, 20.3, None, 40.1, 50.9, 60.7, 70.5, 80.3, 90.1, None],
            'category_col': ['A', 'B', 'A', 'C', 'B', 'A', None, 'C', 'B', 'A'],
            'date_col': pd.date_range(start='2023-01-01', periods=10, freq='D'),
            'string_col': ['text1', 'text2', 'text3', None, 'text5', 
                           'text6', 'text7', 'text8', 'text9', 'text10']
        })

    @pytest.fixture
    def visualizer(self):
        """Create a DataVisualizer instance."""
        return DataVisualizer(fig_size=(10, 6), dpi=100)

    def test_init(self):
        """Test initializing the DataVisualizer."""
        # Test with default values
        visualizer = DataVisualizer()
        assert visualizer.fig_size == (12, 8)
        assert visualizer.dpi == 100
        assert set(visualizer.output_formats) == {'png', 'pdf'}
        
        # Test with custom values
        visualizer = DataVisualizer(fig_size=(8, 6), dpi=200, output_formats=['svg', 'jpg'])
        assert visualizer.fig_size == (8, 6)
        assert visualizer.dpi == 200
        assert set(visualizer.output_formats) == {'svg', 'jpg'}

    def test_create_figure(self, visualizer):
        """Test creating a figure with the visualizer."""
        fig, ax = visualizer.create_figure()
        assert isinstance(fig, plt.Figure)
        assert isinstance(ax, plt.Axes)
        assert fig.get_figwidth() == visualizer.fig_size[0]
        assert fig.get_figheight() == visualizer.fig_size[1]
        plt.close(fig)

    def test_visualize(self, visualizer, sample_dataframe):
        """Test the main visualize method."""
        fig = visualizer.visualize(sample_dataframe)
        assert isinstance(fig, plt.Figure)
        
        # Should have created a dashboard with multiple subplots
        assert len(fig.axes) >= 3  # At least 3 subplots
        
        plt.close(fig)

    def test_plot_missing_values(self, visualizer, sample_dataframe):
        """Test plotting missing values."""
        fig = visualizer.plot_missing_values(sample_dataframe)
        assert isinstance(fig, plt.Figure)
        
        ax = fig.axes[0]
        assert "Missing Values" in ax.get_title()
        
        plt.close(fig)
        
        # Test with no missing values
        df_no_missing = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': [4, 5, 6]
        })
        fig = visualizer.plot_missing_values(df_no_missing)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_plot_distributions(self, visualizer, sample_dataframe):
        """Test plotting distributions."""
        # Test all numeric columns
        fig = visualizer.plot_distributions(sample_dataframe)
        assert isinstance(fig, plt.Figure)
        
        ax = fig.axes[0]
        assert "Distributions" in ax.get_title()
        
        plt.close(fig)
        
        # Test with specific columns
        fig = visualizer.plot_distributions(sample_dataframe, columns=['numeric_col1'])
        assert isinstance(fig, plt.Figure)
        plt.close(fig)
        
        # Test with no numeric columns
        df_no_numeric = pd.DataFrame({
            'col1': ['a', 'b', 'c'],
            'col2': ['d', 'e', 'f']
        })
        fig = visualizer.plot_distributions(df_no_numeric)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_plot_dtypes(self, visualizer, sample_dataframe):
        """Test plotting data types."""
        fig = visualizer.plot_dtypes(sample_dataframe)
        assert isinstance(fig, plt.Figure)
        
        ax = fig.axes[0]
        assert "Data Types" in ax.get_title() or "Column Types" in ax.get_title()
        
        plt.close(fig)

    def test_save_visualization(self, visualizer, sample_dataframe, temp_output_dir):
        """Test saving a visualization to disk."""
        # Create a visualization
        fig = visualizer.visualize(sample_dataframe)
        
        # Save it using save_figure from visualization_utils
        # We'll use visualizer.create_figure to create a figure
        # and then use save_figure from the existing module
        from src.visualization.visualization_utils import save_figure
        
        output_path = os.path.join(temp_output_dir, 'data_overview')
        saved_files = save_figure(fig, output_path, formats=visualizer.output_formats)
        
        # Check saved files
        assert len(saved_files) == len(visualizer.output_formats)
        assert all(os.path.exists(f) for f in saved_files)
        
        # Check file extensions match output_formats
        for fmt in visualizer.output_formats:
            assert any(str(f).endswith(f'.{fmt}') for f in saved_files)
            
        plt.close(fig) 