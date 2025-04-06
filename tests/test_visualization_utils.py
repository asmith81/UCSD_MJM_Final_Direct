import os
import tempfile
import pytest
import numpy as np
import pandas as pd
import matplotlib
# Set non-interactive backend for testing
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from PIL import Image

from src.visualization.visualization_utils import (
    configure_matplotlib_defaults,
    create_figure,
    save_figure,
    plot_confusion_matrix,
    plot_field_accuracy_bars,
    plot_image_with_annotations
)


class TestVisualizationUtils:
    """Test suite for visualization utility functions."""

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
    def test_confusion_matrix(self):
        """Create a test confusion matrix."""
        return np.array([
            [10, 2, 1],
            [3, 15, 2],
            [1, 3, 20]
        ])

    @pytest.fixture
    def test_accuracy_data(self):
        """Create test accuracy data."""
        return {
            'field1': 0.95,
            'field2': 0.85,
            'field3': 0.75,
            'field4': 0.65,
            'field5': 0.55
        }

    @pytest.fixture
    def test_image(self):
        """Create a test image."""
        return Image.new('RGB', (200, 200), color=(255, 255, 255))

    @pytest.fixture
    def test_annotations(self):
        """Create test image annotations."""
        return {
            'field1': (10, 10, 50, 50),  # x, y, width, height for box
            'field2': (100, 100, 30, 40),
            'field3': [(150, 50), (170, 60), (160, 80)]  # polygon points
        }

    def test_configure_matplotlib_defaults(self):
        """Test configuration of matplotlib defaults."""
        # Save original rcParams
        original_rcParams = plt.rcParams.copy()
        
        # Configure defaults
        configure_matplotlib_defaults()
        
        # Check that rcParams were updated
        # Note: font.family might be a list in some environments
        assert 'sans-serif' in plt.rcParams['font.family'] 
        assert plt.rcParams['axes.labelsize'] == 12
        assert plt.rcParams['axes.titlesize'] == 14
        
        # Restore original rcParams
        plt.rcParams.update(original_rcParams)

    def test_create_figure(self):
        """Test figure creation."""
        # Test with default parameters
        fig, ax = create_figure()
        assert isinstance(fig, plt.Figure)
        assert isinstance(ax, plt.Axes)
        assert fig.get_figwidth() == 10
        assert fig.get_figheight() == 6
        plt.close(fig)
        
        # Test with custom parameters
        fig, ax = create_figure(figsize=(8, 4), dpi=200)
        assert fig.get_figwidth() == 8
        assert fig.get_figheight() == 4
        assert fig.dpi == 200
        plt.close(fig)

    def test_save_figure(self, temp_output_dir):
        """Test saving figures to disk."""
        # Create a simple figure
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [4, 5, 6])
        
        # Save with default formats
        filename = os.path.join(temp_output_dir, 'test_figure')
        saved_files = save_figure(fig, filename)
        
        # Check that files were created
        assert len(saved_files) == 2  # default formats: png, pdf
        assert all(os.path.exists(f) for f in saved_files)
        assert any(str(f).endswith('.png') for f in saved_files)
        assert any(str(f).endswith('.pdf') for f in saved_files)
        
        # Test with specific format
        filename = os.path.join(temp_output_dir, 'test_figure_single')
        saved_files = save_figure(fig, filename, formats=['png'])
        
        assert len(saved_files) == 1
        assert os.path.exists(saved_files[0])
        assert str(saved_files[0]).endswith('.png')
        
        plt.close(fig)

    def test_plot_confusion_matrix(self, test_confusion_matrix):
        """Test confusion matrix plotting."""
        # Test with default parameters
        class_names = ['Class A', 'Class B', 'Class C']
        fig = plot_confusion_matrix(test_confusion_matrix, class_names)
        
        assert isinstance(fig, plt.Figure)
        ax = fig.axes[0]
        assert ax.get_title() == 'Confusion Matrix'
        assert ax.get_xlabel() == 'Predicted'
        assert ax.get_ylabel() == 'True'
        
        # Check that class names are used for tick labels
        x_tick_labels = [label.get_text() for label in ax.get_xticklabels()]
        y_tick_labels = [label.get_text() for label in ax.get_yticklabels()]
        assert 'Class A' in x_tick_labels
        assert 'Class B' in x_tick_labels
        assert 'Class C' in x_tick_labels
        
        plt.close(fig)
        
        # Test with empty class names and no normalization
        fig = plot_confusion_matrix(test_confusion_matrix, class_names=[], normalize=False)
        plt.close(fig)

    def test_plot_field_accuracy_bars(self, test_accuracy_data):
        """Test field accuracy bar chart plotting."""
        # Test with default parameters
        fig = plot_field_accuracy_bars(test_accuracy_data)
        
        assert isinstance(fig, plt.Figure)
        ax = fig.axes[0]
        assert ax.get_title() == 'Field Extraction Accuracy'
        assert ax.get_xlabel() == 'Accuracy'
        
        # Check that threshold line is present
        lines = [line for line in ax.get_lines() if line.get_linestyle() == '--']
        assert len(lines) == 1  # Threshold line
        assert lines[0].get_xdata()[0] == 0.8  # Default threshold
        
        plt.close(fig)
        
        # Test with custom parameters
        fig = plot_field_accuracy_bars(
            test_accuracy_data,
            title='Custom Title',
            color='#FF0000',
            threshold=0.7
        )
        
        ax = fig.axes[0]
        assert ax.get_title() == 'Custom Title'
        
        # Check custom threshold
        lines = [line for line in ax.get_lines() if line.get_linestyle() == '--']
        assert lines[0].get_xdata()[0] == 0.7
        
        plt.close(fig)
        
        # Test with no threshold
        fig = plot_field_accuracy_bars(test_accuracy_data, threshold=None)
        ax = fig.axes[0]
        lines = [line for line in ax.get_lines() if line.get_linestyle() == '--']
        assert len(lines) == 0  # No threshold line
        
        plt.close(fig)

    def test_plot_image_with_annotations(self, test_image, test_annotations):
        """Test image annotation plotting."""
        # Test with PIL Image
        fig = plot_image_with_annotations(test_image, test_annotations)
        
        assert isinstance(fig, plt.Figure)
        ax = fig.axes[0]
        assert ax.get_title() == 'Annotated Image'
        
        # Check that annotations were added
        patches_list = [p for p in ax.patches if hasattr(p, 'get_width')]
        assert len(patches_list) == 2  # Two box annotations
        
        # Check for line plots (polygon)
        lines = [line for line in ax.get_lines() if len(line.get_xdata()) > 0]
        assert len(lines) == 1  # One polygon
        
        plt.close(fig)
        
        # Test with numpy array
        numpy_img = np.array(test_image)
        fig = plot_image_with_annotations(
            numpy_img,
            test_annotations,
            title='Custom Title',
            box_color='blue'
        )
        
        ax = fig.axes[0]
        assert ax.get_title() == 'Custom Title'
        
        plt.close(fig)
        
        # Test with temporary image file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp_path = tmp.name
            test_image.save(tmp_path)
            
        try:
            fig = plot_image_with_annotations(tmp_path, test_annotations)
            plt.close(fig)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path) 