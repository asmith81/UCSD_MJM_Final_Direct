"""
Calculator for evaluation metrics.
"""
from typing import Dict, Any, List, Callable, Optional, Union
import numpy as np
from collections import defaultdict


class MetricsCalculator:
    """
    Calculator for computing various evaluation metrics for model performance.
    Includes accuracy, precision, recall, F1 score, and other metrics.
    """
    
    def __init__(self):
        """
        Initialize the metrics calculator with default metric functions.
        """
        self._metrics = {
            "accuracy": self._calculate_accuracy,
            "precision": self._calculate_precision,
            "recall": self._calculate_recall,
            "f1": self._calculate_f1,
            "exact_match": self._calculate_exact_match
        }
        
    def register_metric(self, name: str, metric_func: Callable):
        """
        Register a custom metric function.
        
        Args:
            name: Name of the metric
            metric_func: Function to calculate the metric
        """
        self._metrics[name] = metric_func
        
    def calculate_metric(self, metric_name: str, predictions: Dict[str, Any], 
                          ground_truth: Dict[str, Any]) -> float:
        """
        Calculate a specific metric from predictions and ground truth.
        
        Args:
            metric_name: Name of the metric to calculate
            predictions: Model predictions
            ground_truth: Ground truth data
            
        Returns:
            float: Calculated metric value
            
        Raises:
            ValueError: If the metric is not supported
        """
        if metric_name not in self._metrics:
            raise ValueError(f"Unsupported metric: {metric_name}")
            
        return self._metrics[metric_name](predictions, ground_truth)
    
    def calculate_all_metrics(self, predictions: Dict[str, Any], 
                             ground_truth: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate all registered metrics.
        
        Args:
            predictions: Model predictions
            ground_truth: Ground truth data
            
        Returns:
            Dict[str, float]: Dictionary of metric names and values
        """
        results = {}
        for metric_name in self._metrics:
            results[metric_name] = self.calculate_metric(metric_name, predictions, ground_truth)
        return results
    
    def _calculate_accuracy(self, predictions: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """
        Calculate accuracy across all fields.
        
        Args:
            predictions: Model predictions
            ground_truth: Ground truth data
            
        Returns:
            float: Accuracy score (0-1)
        """
        total_fields = 0
        correct_fields = 0
        
        for image_id, gt_fields in ground_truth.items():
            if image_id not in predictions:
                continue
                
            pred_fields = predictions[image_id]
            
            for field_name, gt_value in gt_fields.items():
                if field_name in pred_fields:
                    total_fields += 1
                    if pred_fields[field_name] == gt_value:
                        correct_fields += 1
        
        if total_fields == 0:
            return 0.0
            
        return correct_fields / total_fields
    
    def _calculate_precision(self, predictions: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """
        Calculate precision across all fields.
        
        Args:
            predictions: Model predictions
            ground_truth: Ground truth data
            
        Returns:
            float: Precision score (0-1)
        """
        # Group by field type
        field_metrics = defaultdict(lambda: {"true_positives": 0, "false_positives": 0})
        
        for image_id, pred_fields in predictions.items():
            gt_fields = ground_truth.get(image_id, {})
            
            for field_name, pred_value in pred_fields.items():
                gt_value = gt_fields.get(field_name)
                
                if gt_value is not None:  # Field exists in ground truth
                    if pred_value == gt_value:
                        field_metrics[field_name]["true_positives"] += 1
                    else:
                        field_metrics[field_name]["false_positives"] += 1
                else:  # Field doesn't exist in ground truth
                    field_metrics[field_name]["false_positives"] += 1
        
        # Calculate overall precision
        true_positives = sum(metrics["true_positives"] for metrics in field_metrics.values())
        false_positives = sum(metrics["false_positives"] for metrics in field_metrics.values())
        
        if true_positives + false_positives == 0:
            return 0.0
            
        return true_positives / (true_positives + false_positives)
    
    def _calculate_recall(self, predictions: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """
        Calculate recall across all fields.
        
        Args:
            predictions: Model predictions
            ground_truth: Ground truth data
            
        Returns:
            float: Recall score (0-1)
        """
        # Group by field type
        field_metrics = defaultdict(lambda: {"true_positives": 0, "false_negatives": 0})
        
        for image_id, gt_fields in ground_truth.items():
            pred_fields = predictions.get(image_id, {})
            
            for field_name, gt_value in gt_fields.items():
                pred_value = pred_fields.get(field_name)
                
                if pred_value is not None:  # Field exists in predictions
                    if pred_value == gt_value:
                        field_metrics[field_name]["true_positives"] += 1
                    else:
                        field_metrics[field_name]["false_negatives"] += 1
                else:  # Field doesn't exist in predictions
                    field_metrics[field_name]["false_negatives"] += 1
        
        # Calculate overall recall
        true_positives = sum(metrics["true_positives"] for metrics in field_metrics.values())
        false_negatives = sum(metrics["false_negatives"] for metrics in field_metrics.values())
        
        if true_positives + false_negatives == 0:
            return 0.0
            
        return true_positives / (true_positives + false_negatives)
    
    def _calculate_f1(self, predictions: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """
        Calculate F1 score across all fields.
        
        Args:
            predictions: Model predictions
            ground_truth: Ground truth data
            
        Returns:
            float: F1 score (0-1)
        """
        precision = self._calculate_precision(predictions, ground_truth)
        recall = self._calculate_recall(predictions, ground_truth)
        
        if precision + recall == 0:
            return 0.0
            
        return 2 * (precision * recall) / (precision + recall)
    
    def _calculate_exact_match(self, predictions: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """
        Calculate exact match ratio (all fields must match).
        
        Args:
            predictions: Model predictions
            ground_truth: Ground truth data
            
        Returns:
            float: Exact match ratio (0-1)
        """
        total_images = 0
        exact_matches = 0
        
        for image_id, gt_fields in ground_truth.items():
            if image_id not in predictions:
                total_images += 1
                continue
                
            total_images += 1
            pred_fields = predictions[image_id]
            
            # All fields must match and be present
            if set(gt_fields.keys()) != set(pred_fields.keys()):
                continue
                
            all_match = True
            for field_name, gt_value in gt_fields.items():
                if pred_fields[field_name] != gt_value:
                    all_match = False
                    break
                    
            if all_match:
                exact_matches += 1
        
        if total_images == 0:
            return 0.0
            
        return exact_matches / total_images
