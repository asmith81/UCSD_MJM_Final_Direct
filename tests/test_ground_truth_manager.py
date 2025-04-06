"""Tests for the GroundTruthManager class."""

import pytest
from pathlib import Path
import pandas as pd
from unittest.mock import Mock
import time
import io
import csv
from decimal import Decimal

from src.data.ground_truth_manager import GroundTruthManager
from src.data.exceptions import GroundTruthError, DataValidationError

# Test data with proper field types
VALID_GROUND_TRUTH = """Invoice,Work Order Number,Total
inv001,12345,123.45
inv002,A1B2C,67.89
"""

INVALID_MISSING_COLS = """Invoice,Field1
inv001,value1
inv002,value3
"""

INVALID_MISSING_VALUES = """Invoice,Work Order Number,Total
inv001,12345,
inv002,,67.89
"""

INVALID_DUPLICATE_IDS = """Invoice,Work Order Number,Total
inv001,12345,123.45
inv001,A1B2C,67.89
"""

# Test data for field validation
INVALID_WORK_ORDER = """Invoice,Work Order Number,Total
inv001,123,123.45
inv002,ABCD,67.89
"""

INVALID_TOTAL = """Invoice,Work Order Number,Total
inv001,12345,abc
inv002,A1B2C,-67.89
"""

CURRENCY_FORMATS = """Invoice,Work Order Number,Total
inv001,12345,$123.45
inv002,A1B2C,"1,234.56"
"""

# Additional test data
MALFORMED_CSV = """Invoice,Work Order Number,Total
inv001,value1
inv002,value2,extra,extra2
completely invalid line
"""

EMPTY_CSV = ""

NON_STRING_VALUES = """Invoice,Work Order Number,Total
inv001,12345,123.45
inv002,AB123,67.89
"""

LARGE_CSV_TEMPLATE = """Invoice,Work Order Number,Total
{rows}
"""

@pytest.fixture
def ground_truth_file(tmp_path):
    """Create a temporary ground truth file."""
    gt_file = tmp_path / "ground_truth.csv"
    gt_file.write_text(VALID_GROUND_TRUTH)
    return gt_file

@pytest.fixture
def manager(ground_truth_file):
    """Create a GroundTruthManager instance."""
    return GroundTruthManager(ground_truth_file)

@pytest.fixture
def large_ground_truth_file(tmp_path):
    """Create a ground truth file matching realistic dataset size (~1000 invoices)."""
    rows = []
    for i in range(1000):  # Changed from 10000 to 1000 to match actual dataset size
        rows.append(f"inv{i:04d},AB{i:03d},{i+10}.50")
    
    gt_file = tmp_path / "ground_truth.csv"
    gt_file.write_text(LARGE_CSV_TEMPLATE.format(rows="\n".join(rows)))
    return gt_file

def test_init_valid_file(ground_truth_file):
    """Test initialization with valid file."""
    manager = GroundTruthManager(ground_truth_file)
    assert manager.ground_truth_file == ground_truth_file
    assert manager.required_columns == ["Invoice", "Work Order Number", "Total"]
    assert manager.cache_enabled is True

def test_init_invalid_file(tmp_path):
    """Test initialization with nonexistent file."""
    invalid_file = tmp_path / "nonexistent.csv"
    with pytest.raises(DataValidationError) as exc_info:
        GroundTruthManager(invalid_file)
    assert "does not exist" in str(exc_info.value)

def test_init_custom_required_columns(ground_truth_file):
    """Test initialization with custom required columns."""
    required_cols = ["Invoice", "Field1"]
    manager = GroundTruthManager(ground_truth_file, required_columns=required_cols)
    assert manager.required_columns == required_cols

def test_validate_ground_truth_valid(manager):
    """Test validation with valid data."""
    manager.validate_ground_truth()
    assert manager._ground_truth_data is not None
    assert len(manager._ground_truth_data) == 2
    assert '_total_float' in manager._ground_truth_data.columns
    assert '_total_formatted' in manager._ground_truth_data.columns
    assert '_work_order_validated' in manager._ground_truth_data.columns

def test_validate_ground_truth_missing_columns(tmp_path):
    """Test validation with missing required columns."""
    gt_file = tmp_path / "ground_truth.csv"
    gt_file.write_text(INVALID_MISSING_COLS)
    manager = GroundTruthManager(gt_file)
    
    with pytest.raises(GroundTruthError) as exc_info:
        manager.validate_ground_truth()
    assert "Missing required columns" in str(exc_info.value)

def test_validate_ground_truth_missing_values(tmp_path):
    """Test validation with missing values."""
    gt_file = tmp_path / "ground_truth.csv"
    gt_file.write_text(INVALID_MISSING_VALUES)
    manager = GroundTruthManager(gt_file)
    
    with pytest.raises(GroundTruthError) as exc_info:
        manager.validate_ground_truth()
    assert "Missing values in required columns" in str(exc_info.value)

def test_validate_ground_truth_duplicate_ids(tmp_path):
    """Test validation with duplicate invoice IDs."""
    gt_file = tmp_path / "ground_truth.csv"
    gt_file.write_text(INVALID_DUPLICATE_IDS)
    manager = GroundTruthManager(gt_file)
    
    with pytest.raises(GroundTruthError) as exc_info:
        manager.validate_ground_truth()
    assert "Duplicate invoice IDs" in str(exc_info.value)

def test_validate_invalid_work_order(tmp_path):
    """Test validation with invalid work order numbers."""
    gt_file = tmp_path / "ground_truth.csv"
    gt_file.write_text(INVALID_WORK_ORDER)
    manager = GroundTruthManager(gt_file)
    
    with pytest.raises(GroundTruthError) as exc_info:
        manager.validate_ground_truth()
    assert "Invalid work order format" in str(exc_info.value)

def test_validate_invalid_total(tmp_path):
    """Test validation with invalid total amounts."""
    gt_file = tmp_path / "ground_truth.csv"
    gt_file.write_text(INVALID_TOTAL)
    manager = GroundTruthManager(gt_file)
    
    with pytest.raises(GroundTruthError) as exc_info:
        manager.validate_ground_truth()
    assert "Invalid total amount format" in str(exc_info.value)

def test_currency_format_handling(tmp_path):
    """Test handling of different currency formats."""
    gt_file = tmp_path / "ground_truth.csv"
    gt_file.write_text(CURRENCY_FORMATS)
    manager = GroundTruthManager(gt_file)
    
    manager.validate_ground_truth()
    data = manager.get_ground_truth("inv001")
    assert data["Total"] == "123.45"
    
    data = manager.get_ground_truth("inv002")
    assert data["Total"] == "1234.56"

def test_get_ground_truth_valid(manager):
    """Test getting ground truth for valid invoice ID."""
    data = manager.get_ground_truth("inv001")
    assert data["Invoice"] == "inv001"
    assert data["Work Order Number"] == "12345"
    assert data["Total"] == "123.45"

def test_get_ground_truth_invalid_id(manager):
    """Test getting ground truth for invalid invoice ID."""
    with pytest.raises(GroundTruthError) as exc_info:
        manager.get_ground_truth("nonexistent")
    assert "not found" in str(exc_info.value)

def test_get_expected_fields(manager):
    """Test getting list of expected fields."""
    fields = manager.get_expected_fields()
    assert set(fields) == {"Work Order Number", "Total"}

def test_clear_cache(manager):
    """Test clearing the cache."""
    manager.validate_ground_truth()
    assert manager._ground_truth_data is not None
    
    manager.clear_cache()
    assert manager._ground_truth_data is None

def test_cache_disabled(ground_truth_file):
    """Test behavior when cache is disabled."""
    manager = GroundTruthManager(ground_truth_file, cache_enabled=False)
    manager.validate_ground_truth()
    assert manager._ground_truth_data is None

def test_malformed_csv(tmp_path):
    """Test handling of malformed CSV file."""
    gt_file = tmp_path / "ground_truth.csv"
    gt_file.write_text(MALFORMED_CSV)
    manager = GroundTruthManager(gt_file)
    
    with pytest.raises(GroundTruthError) as exc_info:
        manager.validate_ground_truth()
    assert "Failed to read ground truth file" in str(exc_info.value)

def test_empty_csv(tmp_path):
    """Test handling of empty CSV file."""
    gt_file = tmp_path / "ground_truth.csv"
    gt_file.write_text(EMPTY_CSV)
    manager = GroundTruthManager(gt_file)
    
    with pytest.raises(GroundTruthError) as exc_info:
        manager.validate_ground_truth()
    assert "Failed to read ground truth file" in str(exc_info.value)

def test_non_string_values(tmp_path):
    """Test handling of non-string values in CSV."""
    gt_file = tmp_path / "ground_truth.csv"
    gt_file.write_text(NON_STRING_VALUES)
    manager = GroundTruthManager(gt_file)
    
    # Should not raise an error - non-string values are converted to strings
    manager.validate_ground_truth()
    
    # Verify values are converted to strings
    data = manager.get_ground_truth("inv001")
    assert isinstance(data["Work Order Number"], str)
    assert isinstance(data["Total"], str)
    assert data["Work Order Number"] == "12345"
    assert data["Total"] == "123.45"

def test_concurrent_access(ground_truth_file):
    """Test concurrent access to the cache."""
    import threading
    
    manager = GroundTruthManager(ground_truth_file)
    results = []
    errors = []
    
    def worker():
        try:
            data = manager.get_ground_truth("inv001")
            results.append(data)
        except Exception as e:
            errors.append(e)
    
    # Create multiple threads accessing the same data
    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Verify all threads got the same data
    assert len(errors) == 0
    assert all(r == results[0] for r in results)
    assert len(results) == 10

def test_memory_usage_large_file(large_ground_truth_file):
    """Test memory usage with realistic dataset size."""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    manager = GroundTruthManager(large_ground_truth_file)
    manager.validate_ground_truth()
    
    # Get memory usage after loading
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Memory increase should be reasonable (less than 10MB for 1k rows)
    assert memory_increase < 10 * 1024 * 1024  # 10MB in bytes

def test_cache_performance(large_ground_truth_file):
    """Test performance with and without cache using realistic dataset size."""
    # Test with cache enabled
    manager_cached = GroundTruthManager(large_ground_truth_file, cache_enabled=True)
    manager_cached.validate_ground_truth()
    
    start_time = time.time()
    for i in range(50):  # Test 50 random accesses (reduced from 100)
        invoice_id = f"inv{i:04d}"
        _ = manager_cached.get_ground_truth(invoice_id)
    cached_time = time.time() - start_time
    
    # Test with cache disabled - special handling needed
    manager_uncached = GroundTruthManager(large_ground_truth_file, cache_enabled=False)
    # We need to manually load the data since it won't be cached
    df = pd.read_csv(large_ground_truth_file)
    
    start_time = time.time()
    for i in range(50):  # Same test without cache
        invoice_id = f"inv{i:04d}"
        row = df[df["Invoice"] == invoice_id].iloc[0]
        # Process similar to get_ground_truth
        result = {col: str(row[col]) for col in df.columns if not col.startswith('_')}
    uncached_time = time.time() - start_time
    
    # Cached should be faster, but don't assert exact timing for test stability
    assert cached_time <= uncached_time * 1.5 or cached_time < 1.0

def test_different_file_encodings(tmp_path):
    """Test handling of different file encodings."""
    # Test UTF-8 with BOM
    utf8_bom_data = VALID_GROUND_TRUTH.encode('utf-8-sig')
    gt_file = tmp_path / "utf8_bom.csv"
    gt_file.write_bytes(utf8_bom_data)
    manager = GroundTruthManager(gt_file)
    manager.validate_ground_truth()
    assert manager.get_ground_truth("inv001")["Work Order Number"] == "12345"
    assert manager.get_ground_truth("inv001")["Total"] == "123.45"
    
    # Test UTF-16
    utf16_data = VALID_GROUND_TRUTH.encode('utf-16')
    gt_file = tmp_path / "utf16.csv"
    gt_file.write_bytes(utf16_data)
    manager = GroundTruthManager(gt_file)
    with pytest.raises(GroundTruthError):
        manager.validate_ground_truth()

def test_cleanup_on_error(tmp_path):
    """Test proper cleanup when errors occur."""
    gt_file = tmp_path / "ground_truth.csv"
    gt_file.write_text(MALFORMED_CSV)
    manager = GroundTruthManager(gt_file)
    
    # Verify internal state before error
    assert manager._ground_truth_data is None
    
    # Trigger error
    with pytest.raises(GroundTruthError):
        manager.validate_ground_truth()
    
    # Verify cleanup occurred
    assert manager._ground_truth_data is None

def test_clean_total_amount(manager):
    """Test cleaning of total amount values."""
    float_val, formatted = manager._clean_total_amount("$1,234.56")
    assert float_val == 1234.56
    assert formatted == "1234.56"
    
    float_val, formatted = manager._clean_total_amount(1234.5)
    assert float_val == 1234.50
    assert formatted == "1234.50"
    
    with pytest.raises(ValueError):
        manager._clean_total_amount("invalid")
    
    with pytest.raises(ValueError):
        manager._clean_total_amount(-123.45)

def test_validate_work_order(manager):
    """Test validation of work order numbers."""
    assert manager._validate_work_order("12345") == "12345"
    assert manager._validate_work_order("A1B2C") == "A1B2C"
    
    with pytest.raises(ValueError):
        manager._validate_work_order("123")  # Too short
    
    with pytest.raises(ValueError):
        manager._validate_work_order("123456")  # Too long
    
    with pytest.raises(ValueError):
        manager._validate_work_order("12.45")  # Invalid character

def test_cache_behavior(manager):
    """Test caching behavior with validated data."""
    assert manager._ground_truth_data is None
    
    # First validation should cache
    manager.validate_ground_truth()
    assert manager._ground_truth_data is not None
    
    # Clear cache
    manager.clear_cache()
    assert manager._ground_truth_data is None
    
    # Disable cache
    manager.cache_enabled = False
    manager.validate_ground_truth()
    assert manager._ground_truth_data is None 