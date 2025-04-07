"""
Tests for the EvaluationService implementation.
"""
import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from src.evaluation.evaluation_service import EvaluationService
from src.config import ConfigType

class TestEvaluationService:
    """Tests for EvaluationService implementation."""
    
    @pytest.fixture
    def mock_metrics_calculator(self):
        """Create a mock metrics calculator."""
        calculator = Mock()
        calculator.calculate_metric.return_value = 0.85  # Mock accuracy score
        return calculator
    
    @pytest.fixture
    def mock_results_manager(self):
        """Create a mock results manager."""
        manager = Mock()
        manager.load_ground_truth.return_value = {"test_image": {"field1": "value1"}}
        manager.load_results.return_value = {"accuracy": 0.85, "f1": 0.78}
        return manager
    
    @pytest.fixture
    def mock_config_manager(self):
        """Create a mock config manager."""
        manager = Mock()
        mock_config = Mock()
        mock_config.get_metrics.return_value = ["accuracy", "f1"]
        mock_config.get_dataset_path.return_value = "/path/to/dataset"
        mock_config.get_output_format.return_value = "json"
        
        manager.get_config.return_value = mock_config
        return manager
    
    @pytest.fixture
    def evaluation_service(self, mock_metrics_calculator, mock_results_manager, mock_config_manager):
        """Create an EvaluationService instance for testing."""
        return EvaluationService(
            mock_metrics_calculator, 
            mock_results_manager,
            mock_config_manager
        )
    
    def test_service_initialization(self, mock_metrics_calculator, mock_results_manager, mock_config_manager):
        """Test service initialization."""
        service = EvaluationService(
            mock_metrics_calculator, 
            mock_results_manager,
            mock_config_manager
        )
        
        assert service.metrics_calculator == mock_metrics_calculator
        assert service.results_manager == mock_results_manager
        assert service._config_manager == mock_config_manager
        
        # Verify config was loaded
        mock_config_manager.get_config.assert_called_once_with(ConfigType.EVALUATION)
        assert service.metrics == ["accuracy", "f1"]
        assert service.dataset_path == Path("/path/to/dataset")
        assert service.output_format == "json"
    
    def test_service_initialization_fails_without_dependencies(self):
        """Test that service requires all dependencies."""
        mock_calculator = Mock()
        mock_manager = Mock()
        mock_config = Mock()
        
        with pytest.raises(ValueError, match="All dependencies.*are required"):
            EvaluationService(None, mock_manager, mock_config)
            
        with pytest.raises(ValueError, match="All dependencies.*are required"):
            EvaluationService(mock_calculator, None, mock_config)
            
        with pytest.raises(ValueError, match="All dependencies.*are required"):
            EvaluationService(mock_calculator, mock_manager, None)
    
    def test_evaluate_model(self, evaluation_service, mock_metrics_calculator, mock_results_manager):
        """Test model evaluation."""
        # Define test data
        model_name = "test_model"
        predictions = {"test_image": {"field1": "predicted_value"}}
        
        # Call the method
        results = evaluation_service.evaluate_model(model_name, predictions)
        
        # Verify correct calls were made
        mock_results_manager.load_ground_truth.assert_called_once()
        assert mock_metrics_calculator.calculate_metric.call_count == 2  # Two metrics
        mock_results_manager.save_results.assert_called_once_with(
            model_name, 
            {"accuracy": 0.85, "f1": 0.85},  # Both metrics return 0.85
            format="json"
        )
        
        # Verify correct results were returned
        assert results == {"accuracy": 0.85, "f1": 0.85}
    
    def test_get_model_performance(self, evaluation_service, mock_results_manager):
        """Test retrieving model performance."""
        model_name = "test_model"
        
        # Call the method
        results = evaluation_service.get_model_performance(model_name)
        
        # Verify correct calls were made
        mock_results_manager.load_results.assert_called_once_with(model_name)
        
        # Verify correct results were returned
        assert results == {"accuracy": 0.85, "f1": 0.78}
    
    def test_compare_models(self, evaluation_service, mock_results_manager):
        """Test comparing multiple models."""
        model_names = ["model1", "model2"]
        
        # Call the method
        results = evaluation_service.compare_models(model_names)
        
        # Verify correct calls were made
        assert mock_results_manager.load_results.call_count == 2
        
        # Verify correct results were returned
        assert results == {
            "model1": {"accuracy": 0.85, "f1": 0.78},
            "model2": {"accuracy": 0.85, "f1": 0.78}
        } 