import os
import tempfile
import pytest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from PIL import Image

from src.data.validation_utils import (
    validate_csv_file,
    validate_image_directory,
    get_data_statistics,
    validate_extracted_fields
)
from src.data.validators.field_validators import (
    compare_extracted_to_ground_truth
)
from src.visualization.visualization_utils import (
    plot_field_accuracy_bars,
    plot_image_with_annotations,
    save_figure
)


class TestValidationVisualizationIntegration:
    """Integration tests for validation and visualization utilities."""

    @pytest.fixture
    def temp_test_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Close all matplotlib figures
        plt.close('all')
        # Give a moment for resources to release
        import time
        time.sleep(0.5)
        # Clean up
        if os.path.exists(temp_dir):
            import shutil
            try:
                shutil.rmtree(temp_dir)
            except PermissionError:
                print(f"Warning: Could not fully clean up {temp_dir}")

    @pytest.fixture
    def sample_data_df(self):
        """Create a sample DataFrame with invoice data."""
        return pd.DataFrame({
            'invoice_id': [f'INV-{i:04d}' for i in range(1, 11)],
            'total_amount': ['$123.45', '$234.56', '$345.67', '$456.78', '$567.89',
                             '$678.90', '$789.01', '$890.12', '$901.23', '$1,012.34'],
            'work_order': ['AB123', 'CD456', 'EF789', 'GH012', 'IJ345',
                           'KL678', 'MN901', 'OP234', 'QR567', 'ST890'],
            'date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
                    '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10'],
            'extracted_confidence': [0.95, 0.87, 0.92, 0.78, 0.85, 0.91, 0.88, 0.79, 0.83, 0.93]
        })

    @pytest.fixture
    def sample_csv_file(self, temp_test_dir, sample_data_df):
        """Create a sample CSV file with invoice data."""
        csv_path = os.path.join(temp_test_dir, 'sample_invoices.csv')
        sample_data_df.to_csv(csv_path, index=False)
        return csv_path

    @pytest.fixture
    def sample_image_dir(self, temp_test_dir):
        """Create a sample directory with invoice images."""
        img_dir = os.path.join(temp_test_dir, 'images')
        os.makedirs(img_dir, exist_ok=True)
        
        # Create 5 sample invoice images
        for i in range(5):
            # Create a white background
            img = Image.new('RGB', (800, 1000), color=(255, 255, 255))
            img_path = os.path.join(img_dir, f'invoice_{i+1}.png')
            img.save(img_path)
            
        return img_dir

    @pytest.fixture
    def sample_extracted_data(self):
        """Create a sample of extracted invoice data."""
        return [
            {
                'invoice_id': 'INV-0001',
                'total_amount': '$123.45',
                'work_order': 'AB123',
                'date': '2023-01-01',
                'vendor': 'Acme Inc'
            },
            {
                'invoice_id': 'INV-0002',
                'total_amount': '$234.56',
                'work_order': 'CD456',
                'date': '2023-01-02',
                'vendor': 'Beta Corp'
            },
            {
                'invoice_id': 'INV-0003',
                'total_amount': '345.67',  # No $ sign
                'work_order': 'EF789',
                'date': '2023-01-03',
                'purchase_order': 'PO-12345'  # Additional field
            }
        ]

    @pytest.fixture
    def sample_ground_truth(self):
        """Create a sample of ground truth invoice data."""
        return [
            {
                'invoice_id': 'INV-0001',
                'total_amount': '123.45',  # No $ sign
                'work_order': 'AB123',
                'date': '2023-01-01',
                'vendor': 'Acme Inc'
            },
            {
                'invoice_id': 'INV-0002',
                'total_amount': '234.56',  # No $ sign
                'work_order': 'CD456',
                'date': '2023-01-02',
                'vendor': 'Beta Corporation'  # Different name
            },
            {
                'invoice_id': 'INV-0003',
                'total_amount': '345.67',
                'work_order': 'EF789',
                'date': '2023/01/03',  # Different format
                'customer': 'Gamma LLC'  # Different field
            }
        ]

    def test_validation_to_visualization_flow(self, sample_csv_file, temp_test_dir):
        """Test the complete flow from data validation to visualization."""
        # Step 1: Validate CSV file
        is_valid, error_msg, df = validate_csv_file(sample_csv_file)
        assert is_valid is True
        assert error_msg == ""
        assert isinstance(df, pd.DataFrame)
        
        # Step 2: Get data statistics
        stats = get_data_statistics(df)
        assert "shape" in stats
        assert stats["shape"][0] == 10  # 10 rows
        
        # Step 3: Calculate field accuracy - simulating extraction accuracy
        field_accuracy = {
            'total_amount': df['extracted_confidence'].mean(),
            'work_order': df['extracted_confidence'].mean() * 0.95,
            'date': df['extracted_confidence'].mean() * 0.9,
            'invoice_id': df['extracted_confidence'].mean() * 0.98,
        }
        
        # Step 4: Visualize field accuracy
        fig = plot_field_accuracy_bars(field_accuracy, 
                                      title='Field Extraction Accuracy')
        
        # Step 5: Save visualization
        output_path = os.path.join(temp_test_dir, 'field_accuracy')
        saved_files = save_figure(fig, output_path)
        
        assert len(saved_files) > 0
        assert all(os.path.exists(f) for f in saved_files)
        
        plt.close(fig)

    def test_extracted_vs_ground_truth_visualization(self, sample_extracted_data, sample_ground_truth, temp_test_dir):
        """Test validation of extracted data against ground truth and visualizing results."""
        # Initialize results storage
        match_results = {
            'exact_matches': {},
            'normalized_matches': {},
            'missing_in_extracted': {},
            'missing_in_ground_truth': {}
        }
        
        # Process each pair of documents
        for i, (extracted, ground_truth) in enumerate(zip(sample_extracted_data, sample_ground_truth)):
            # Step 1: Validate extracted fields against ground truth
            validation_results = validate_extracted_fields(extracted, ground_truth)
            
            # Step 2: Store metrics for visualization
            doc_id = f"doc_{i+1}"
            match_results['exact_matches'][doc_id] = validation_results['exact_match_rate']
            match_results['normalized_matches'][doc_id] = validation_results['normalized_match_rate']
            
            # Count missing fields
            match_results['missing_in_extracted'][doc_id] = len(validation_results['missing_in_extracted'])
            match_results['missing_in_ground_truth'][doc_id] = len(validation_results['missing_in_ground_truth'])
        
        # Step 3: Create visualizations for each metric
        for metric, values in match_results.items():
            if metric in ['exact_matches', 'normalized_matches']:
                # Create accuracy bar chart
                fig = plot_field_accuracy_bars(
                    values,
                    title=f'{metric.replace("_", " ").title()} by Document',
                    threshold=0.8 if 'matches' in metric else None
                )
                
                # Save the figure
                output_path = os.path.join(temp_test_dir, f'{metric}_chart')
                save_figure(fig, output_path)
                plt.close(fig)
        
        # Check that files were created
        assert os.path.exists(os.path.join(temp_test_dir, 'exact_matches_chart.png'))
        assert os.path.exists(os.path.join(temp_test_dir, 'normalized_matches_chart.png'))

    def test_image_validation_and_annotation(self, sample_image_dir, temp_test_dir):
        """Test validation of images and annotation visualization."""
        # Step 1: Validate image directory
        validation_result = validate_image_directory(sample_image_dir)
        assert validation_result["valid"] is True
        assert validation_result["image_count"] == 5
        
        # Step 2: Create sample bounding box annotations
        # In a real scenario, these might come from OCR or model predictions
        sample_annotations = {
            'total_amount': (300, 200, 100, 30),
            'invoice_number': (100, 100, 120, 30),
            'date': (500, 100, 80, 30),
            'table_region': [(200, 400), (200, 600), (600, 600), (600, 400)]
        }
        
        # Step 3: Load a sample image
        sample_image_path = os.path.join(sample_image_dir, 'invoice_1.png')
        img = Image.open(sample_image_path)
        
        try:
            # Step 4: Create annotated visualization
            fig = plot_image_with_annotations(
                img,
                sample_annotations,
                title='Invoice Fields Detection'
            )
            
            # Step 5: Save visualization
            output_path = os.path.join(temp_test_dir, 'annotated_invoice')
            saved_files = save_figure(fig, output_path)
            
            assert len(saved_files) > 0
            assert all(os.path.exists(f) for f in saved_files)
        finally:
            # Ensure we close the image and the figure
            plt.close('all')
            img.close() 