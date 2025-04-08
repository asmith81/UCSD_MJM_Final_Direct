"""
Manager for evaluation results and ground truth data.
"""
import json
import yaml
import csv
import pickle
from typing import Dict, Any, List, Optional
from pathlib import Path


class ResultsManager:
    """
    Manager for loading and saving evaluation results and ground truth data.
    Supports multiple output formats and structured result organization.
    """
    
    SUPPORTED_FORMATS = ["json", "yaml", "csv", "pickle"]
    
    def __init__(self, results_dir: Optional[str] = None):
        """
        Initialize the results manager with a results directory.
        
        Args:
            results_dir: Directory for storing results. If None, uses "results" directory.
        """
        self.results_dir = Path(results_dir) if results_dir else Path("results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def save_results(self, model_name: str, results: Dict[str, float], 
                     format: str = "json") -> Path:
        """
        Save evaluation results for a model.
        
        Args:
            model_name: Name of the model
            results: Dictionary of metric names and values
            format: Output format (json, yaml, csv, pickle)
            
        Returns:
            Path: Path to the saved results file
            
        Raises:
            ValueError: If the format is not supported
        """
        if format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {format}. Supported formats: {self.SUPPORTED_FORMATS}")
        
        # Create model directory
        model_dir = self.results_dir / model_name
        model_dir.mkdir(exist_ok=True)
        
        # Create file path
        file_path = model_dir / f"metrics.{format}"
        
        # Save results in the specified format
        if format == "json":
            with open(file_path, 'w') as f:
                json.dump(results, f, indent=2)
                
        elif format == "yaml":
            with open(file_path, 'w') as f:
                yaml.dump(results, f)
                
        elif format == "csv":
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["metric", "value"])
                for metric, value in results.items():
                    writer.writerow([metric, value])
                    
        elif format == "pickle":
            with open(file_path, 'wb') as f:
                pickle.dump(results, f)
        
        return file_path
    
    def load_results(self, model_name: str) -> Dict[str, float]:
        """
        Load evaluation results for a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dict[str, float]: Dictionary of metric names and values
            
        Raises:
            FileNotFoundError: If the results file does not exist
        """
        # Check each supported format
        model_dir = self.results_dir / model_name
        
        for format in self.SUPPORTED_FORMATS:
            file_path = model_dir / f"metrics.{format}"
            
            if file_path.exists():
                # Load results based on format
                if format == "json":
                    with open(file_path, 'r') as f:
                        return json.load(f)
                        
                elif format == "yaml":
                    with open(file_path, 'r') as f:
                        return yaml.safe_load(f)
                        
                elif format == "csv":
                    results = {}
                    with open(file_path, 'r', newline='') as f:
                        reader = csv.reader(f)
                        next(reader)  # Skip header
                        for row in reader:
                            metric, value = row
                            results[metric] = float(value)
                    return results
                    
                elif format == "pickle":
                    with open(file_path, 'rb') as f:
                        return pickle.load(f)
        
        raise FileNotFoundError(f"No results found for model: {model_name}")
    
    def load_ground_truth(self, dataset_path: Path) -> Dict[str, Any]:
        """
        Load ground truth data from dataset.
        
        Args:
            dataset_path: Path to the dataset directory or file
            
        Returns:
            Dict[str, Any]: Ground truth data
            
        Raises:
            FileNotFoundError: If the dataset file does not exist
        """
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")
        
        # If path is a directory, look for ground truth file
        if dataset_path.is_dir():
            for ext in ["json", "yaml", "csv", "pickle"]:
                file_path = dataset_path / f"ground_truth.{ext}"
                if file_path.exists():
                    dataset_path = file_path
                    break
        
        # Load ground truth based on file extension
        if dataset_path.suffix == ".json":
            with open(dataset_path, 'r') as f:
                return json.load(f)
                
        elif dataset_path.suffix in [".yaml", ".yml"]:
            with open(dataset_path, 'r') as f:
                return yaml.safe_load(f)
                
        elif dataset_path.suffix == ".csv":
            # Assume CSV structure: image_id, field_name, field_value
            results = {}
            with open(dataset_path, 'r', newline='') as f:
                reader = csv.reader(f)
                header = next(reader)
                for row in reader:
                    image_id, field_name, field_value = row[:3]
                    if image_id not in results:
                        results[image_id] = {}
                    results[image_id][field_name] = field_value
            return results
            
        elif dataset_path.suffix == ".pickle":
            with open(dataset_path, 'rb') as f:
                return pickle.load(f)
        
        else:
            raise ValueError(f"Unsupported file format: {dataset_path.suffix}")
    
    def delete_results(self, model_name: str) -> bool:
        """
        Delete evaluation results for a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            bool: True if results were deleted, False if they didn't exist
        """
        model_dir = self.results_dir / model_name
        
        if not model_dir.exists():
            return False
        
        # Delete all result files
        deleted = False
        for format in self.SUPPORTED_FORMATS:
            file_path = model_dir / f"metrics.{format}"
            if file_path.exists():
                file_path.unlink()
                deleted = True
        
        # Remove directory if empty
        if not any(model_dir.iterdir()):
            model_dir.rmdir()
        
        return deleted
