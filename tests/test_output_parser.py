"""
Tests for the output parser components.

This module contains tests for the output parser interfaces, factory, and implementations.
"""
import pytest
from typing import Dict, Any
import json
import re
from unittest.mock import MagicMock, patch, Mock
from unittest import mock

from src.models import (
    BaseOutputParser,
    OutputParserError,
    OutputParsingError,
    OutputValidationError,
    OutputParserFactory,
    OutputParserCreationError
)
from src.models.output_parser_factory import OutputParserCreationError
from src.data.validators.extracted_data_validator import ExtractedDataValidator
from src.models.output_parser.implementations import ExtractedFieldsOutputParser


class MockValidator(ExtractedDataValidator):
    """Mock validator for testing."""
    
    def __init__(self, should_validate: bool = True):
        super().__init__(expected_fields=[], strict_mode=False)
        self.should_validate = should_validate
        
    def validate(self, data: Dict[str, Any]) -> bool:
        """Mock validation that returns the configured value."""
        return self.should_validate


class MockConfigManager:
    """Mock configuration manager for testing."""
    
    def get_config(self, *args, **kwargs):
        """Return a mock config."""
        return MagicMock()


# Mock parser for testing
class MockParser(BaseOutputParser):
    """Mock parser implementation for testing."""
    
    def __init__(self):
        self.initialized = False
        self.config = None
    
    def initialize(self, config):
        self.initialized = True
        self.config = config
        
    def parse_output(self, output_text):
        return {"mock": "result"}
        
    def format_output(self, parsed_data):
        return parsed_data
        
    def validate_output(self, parsed_output):
        """Mock validate_output implementation."""
        return True
        
    def normalize_output(self, parsed_output):
        """Mock normalize_output implementation."""
        return parsed_output


class TestOutputParserInterface:
    """Tests for the output parser interface and factory."""
    
    @pytest.fixture
    def mock_get_config_manager(self):
        """Mock the config manager."""
        mock_config_manager = Mock()
        return mock_config_manager

    @pytest.fixture
    def factory(self, mock_get_config_manager):
        """Create an OutputParserFactory for testing."""
        return OutputParserFactory(mock_get_config_manager)

    def test_factory_registration(self, factory):
        """Test registration of parser implementations."""
        # Clear registry first
        OutputParserFactory.PARSER_REGISTRY.clear()
        
        # Register a parser implementation
        OutputParserFactory.register_parser("test_parser", MockParser)
        
        # Verify it's in the registry
        assert "test_parser" in OutputParserFactory.PARSER_REGISTRY
        assert OutputParserFactory.PARSER_REGISTRY["test_parser"] == MockParser

    def test_factory_invalid_registration(self, factory):
        """Test invalid registrations."""
        # Invalid parser type
        with pytest.raises(ValueError):
            OutputParserFactory.register_parser("", MockParser)
        
        # Invalid parser class (not a BaseOutputParser)
        with pytest.raises(ValueError):
            OutputParserFactory.register_parser("invalid", object)

    def test_factory_create_parser(self, factory):
        """Test creation of parser instances."""
        # Register a parser
        OutputParserFactory.PARSER_REGISTRY.clear()
        OutputParserFactory.register_parser("test_parser", MockParser)
        
        # Create a parser
        parser = factory.create_parser("test_parser")
        
        # Verify the parser was created
        assert isinstance(parser, MockParser)
        assert not parser.initialized  # No config provided

    def test_factory_create_parser_with_config(self, factory):
        """Test creation of parser with config."""
        # Register a parser
        OutputParserFactory.PARSER_REGISTRY.clear()
        OutputParserFactory.register_parser("test_parser", MockParser)
        
        # Create a parser with config
        config = Mock()
        parser = factory.create_parser("test_parser", config)
        
        # Verify the parser was initialized
        assert isinstance(parser, MockParser)
        assert parser.initialized
        assert parser.config == config

    def test_factory_unknown_parser(self, factory):
        """Test creation with unknown parser type."""
        OutputParserFactory.PARSER_REGISTRY.clear()
        
        # Try to create unknown parser
        with pytest.raises(OutputParserCreationError, match="Unsupported parser type"):
            factory.create_parser("unknown_parser")

    def test_factory_requires_config_manager(self):
        """Test that factory requires config_manager."""
        with pytest.raises(ValueError, match="config_manager is required"):
            OutputParserFactory(None)


class TestExtractedFieldsOutputParser:
    """Tests for the ExtractedFieldsOutputParser implementation."""
    
    @pytest.fixture
    def parser(self):
        """Create a parser instance for testing."""
        return ExtractedFieldsOutputParser()
    
    @pytest.fixture
    def mock_validator(self):
        """Create a mock validator that always validates."""
        return MockValidator(should_validate=True)
    
    @pytest.fixture
    def parser_with_mock(self, mock_validator):
        """Create a parser with mock validator."""
        return ExtractedFieldsOutputParser(data_validator=mock_validator)
    
    def test_field_name_normalization(self, parser):
        """Test field name normalization."""
        # Test work order variants
        assert parser._normalize_field_name("work order") == "work_order"
        assert parser._normalize_field_name("Work Order Number") == "work_order"
        assert parser._normalize_field_name("workorder") == "work_order"
        assert parser._normalize_field_name("wo #") == "work_order"
        
        # Test total amount variants
        assert parser._normalize_field_name("total amount") == "total_amount"
        assert parser._normalize_field_name("Total") == "total_amount"
        assert parser._normalize_field_name("invoice total") == "total_amount"
        
        # Test unknown field
        assert parser._normalize_field_name("unknown field") == "unknown field"
    
    def test_json_parsing(self, parser):
        """Test JSON parsing."""
        # Test with simple JSON
        json_output = '{"work_order": "12345", "total_amount": 123.45}'
        parsed = parser._try_json_parsing(json_output)
        assert parsed == {"work_order": "12345", "total_amount": 123.45}
        
        # Test with JSON embedded in text
        mixed_output = 'The extracted fields are: {"work_order": "12345", "total_amount": 123.45} from the invoice.'
        parsed = parser._try_json_parsing(mixed_output)
        assert parsed == {"work_order": "12345", "total_amount": 123.45}
        
        # Test with invalid JSON
        invalid_json = 'This is not JSON'
        parsed = parser._try_json_parsing(invalid_json)
        assert parsed is None
    
    def test_key_value_parsing(self, parser):
        """Test key-value parsing."""
        # Test with simple key-value pairs
        kv_output = 'Work Order: 12345, Total Amount: $123.45'
        parsed = parser._try_key_value_parsing(kv_output)
        assert parsed == {"work_order": "12345", "total_amount": "$123.45"}
        
        # Test with newlines
        kv_output = 'Work Order: 12345\nTotal Amount: $123.45'
        parsed = parser._try_key_value_parsing(kv_output)
        assert parsed == {"work_order": "12345", "total_amount": "$123.45"}
        
        # Test with no valid key-value pairs
        invalid_kv = 'This has no key-value pairs'
        parsed = parser._try_key_value_parsing(invalid_kv)
        assert parsed is None
    
    def test_parse_output(self, parser):
        """Test the main parse_output method."""
        # Test with JSON
        json_output = '{"work_order": "12345", "total_amount": 123.45}'
        parsed = parser.parse_output(json_output)
        assert parsed == {"work_order": "12345", "total_amount": 123.45}
        
        # Test with key-value
        kv_output = 'Work Order: 12345, Total Amount: $123.45'
        parsed = parser.parse_output(kv_output)
        assert parsed == {"work_order": "12345", "total_amount": "$123.45"}
        
        # Test with invalid input
        with pytest.raises(OutputParsingError):
            parser.parse_output("This can't be parsed")
    
    def test_normalize_output(self, parser):
        """Test output normalization."""
        # Input with non-normalized field names and values
        input_data = {
            "Work Order": "12345",
            "Total": "$123.45"
        }
        
        normalized = parser.normalize_output(input_data)
        
        # Field names should be normalized
        assert "work_order" in normalized
        assert "total_amount" in normalized
        
        # Values should be processed by field validators
        # Note: We can't assert exact values without mocking validators
    
    def test_validate_output(self, parser_with_mock, mock_validator):
        """Test output validation with mock validator."""
        # Set mock validator to validate successfully
        mock_validator.should_validate = True
        
        # Test validation passes
        assert parser_with_mock.validate_output({"work_order": "12345"})
        
        # Set mock validator to fail validation
        mock_validator.should_validate = False
        
        # Test validation fails
        assert not parser_with_mock.validate_output({"work_order": "12345"}) 