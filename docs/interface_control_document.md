# Interface Control Document (ICD)

## Overview
This document defines the interfaces and interactions between major components of the LMM Invoice Data Extraction Comparison system. It serves as the authoritative source for interface specifications and component interactions.

## 1. Configuration System ✓

### 1.1 Base Configuration Interface
```python
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseConfig(ABC):
    """Base interface for all configuration implementations."""
    
    @abstractmethod
    def get_data(self) -> Dict[str, Any]:
        """Get the configuration data.
        
        Returns:
            Dict[str, Any]: The configuration data
        """
        pass
```

### 1.2 Configuration Parser Protocol
```python
from typing import Protocol
from pathlib import Path
from typing import Dict, Any

class ConfigParser(Protocol):
    """Protocol defining the interface for configuration parsers."""
    
    def load(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration from a file.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            Dict[str, Any]: The parsed configuration data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file cannot be parsed
        """
        ...
```

### 1.3 Configuration Factory
```python
from typing import Dict, Type
from src.config.base_config import BaseConfig

class ConfigFactory:
    """Factory for creating configuration objects."""
    
    def create_model_config(self, data: Dict[str, Any]) -> BaseConfig:
        """Create a model configuration instance."""
        pass
    
    def create_prompt_config(self, data: Dict[str, Any]) -> BaseConfig:
        """Create a prompt configuration instance."""
        pass
    
    def create_evaluation_config(self, data: Dict[str, Any]) -> BaseConfig:
        """Create an evaluation configuration instance."""
        pass
```

### 1.4 Configuration Loader
```python
from pathlib import Path
from typing import Optional
from src.config.base_config import BaseConfig

class ConfigLoader:
    """Loads and manages configuration files."""
    
    def __init__(
        self,
        config_path: Path,
        config_factory: ConfigFactory,
        config_parser: Optional[ConfigParser] = None
    ) -> None:
        """Initialize the configuration loader.
        
        Args:
            config_path: Base path for configuration files
            config_factory: Factory for creating config objects
            config_parser: Parser for loading config files (optional)
        """
        pass
    
    def load_model_config(self, model_name: str) -> BaseConfig:
        """Load model configuration."""
        pass
    
    def load_prompt_config(self, prompt_name: str) -> BaseConfig:
        """Load prompt configuration."""
        pass
    
    def load_evaluation_config(self) -> BaseConfig:
        """Load evaluation configuration."""
        pass
```

## 2. Image Processing System ✓

### 2.1 Image Processor Configuration
```python
from dataclasses import dataclass
from typing import Tuple, Optional
from enum import Enum

class ColorMode(Enum):
    """Supported color modes for image processing."""
    RGB = "RGB"
    GRAYSCALE = "L"

@dataclass
class ImageProcessorConfig:
    """Configuration for image preprocessing operations."""
    target_size: Tuple[int, int] = (1024, 1365)
    color_mode: ColorMode = ColorMode.RGB
    normalize: bool = True
    maintain_aspect_ratio: bool = True
    jpeg_quality: int = 95
    contrast_factor: Optional[float] = None
    brightness_factor: Optional[float] = None
    sharpness_factor: Optional[float] = None
```

### 2.2 Base Image Processor Interface
```python
from abc import ABC, abstractmethod
from typing import List
from PIL import Image
from src.config.base_config import BaseConfig

class BaseImageProcessor(ABC):
    """Base interface for image preprocessing operations."""
    
    @abstractmethod
    def initialize(self, config: BaseConfig) -> None:
        """Initialize the image processor with configuration.
        
        Args:
            config: Image processor configuration
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        pass
        
    @abstractmethod
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess a single image according to configuration.
        
        Args:
            image: Input PIL Image
            
        Returns:
            Image.Image: Preprocessed image
            
        Raises:
            ImageProcessingError: If processing fails
        """
        pass
        
    @abstractmethod
    def batch_preprocess(self, images: List[Image.Image]) -> List[Image.Image]:
        """Preprocess multiple images.
        
        Args:
            images: List of input PIL Images
            
        Returns:
            List[Image.Image]: List of preprocessed images
            
        Raises:
            ImageProcessingError: If processing fails
        """
        pass
        
    @abstractmethod
    def validate_image(self, image: Image.Image) -> bool:
        """Validate that an image meets processing requirements.
        
        Args:
            image: Input PIL Image
            
        Returns:
            bool: True if image is valid, False otherwise
        """
        pass
```

### 2.3 Image Processor Factory
```python
from typing import Dict, Type
from src.image.base_image_processor import BaseImageProcessor
from src.config.base_config import BaseConfig

class ImageProcessorFactory:
    """Factory for creating image processor instances."""
    
    REGISTRY: Dict[str, Type[BaseImageProcessor]] = {}
    
    def create_processor(
        self,
        processor_type: str,
        config: BaseConfig
    ) -> BaseImageProcessor:
        """Create an image processor instance.
        
        Args:
            processor_type: Type of processor to create
            config: Processor configuration
            
        Returns:
            BaseImageProcessor: The created processor instance
            
        Raises:
            ValueError: If processor_type is not supported
        """
        pass
```

## 3. Model System (In Progress)

### 3.1 Base Model Interface ✓
```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

from ..config.base_config import BaseConfig


class ModelInitializationError(Exception):
    """Raised when a model fails to initialize properly."""
    pass


class ModelProcessingError(Exception):
    """Raised when a model fails to process an image."""
    pass


class BaseModel(ABC):
    """Base interface for all model implementations.
    
    This class defines the interface that all model implementations must follow.
    Models are responsible for:
    1. Initializing with configuration
    2. Processing invoice images
    3. Returning structured results
    4. Managing their own resources
    
    Implementations should:
    - Handle their own resource management
    - Implement proper error handling
    - Clean up resources when errors occur
    - Validate inputs before processing
    """
    
    @abstractmethod
    def initialize(self, config: BaseConfig) -> None:
        """Initialize the model with configuration.
        
        This method should:
        1. Validate the configuration
        2. Load model weights/resources
        3. Set up any required processing pipelines
        
        Args:
            config: Model configuration implementing BaseConfig
            
        Raises:
            ModelInitializationError: If initialization fails
            ValueError: If configuration is invalid
        """
        pass
        
    @abstractmethod
    def process_image(self, image_path: Path) -> Dict[str, Any]:
        """Process an invoice image and extract information.
        
        This method should:
        1. Validate the input image
        2. Preprocess the image as needed
        3. Run inference
        4. Post-process and structure the results
        
        Args:
            image_path: Path to the invoice image file
            
        Returns:
            Dict containing extracted information with standardized keys
            
        Raises:
            ModelProcessingError: If processing fails
            FileNotFoundError: If image file doesn't exist
            ValueError: If image is invalid or corrupted
        """
        pass
        
    @abstractmethod
    def validate_config(self, config: BaseConfig) -> bool:
        """Validate model-specific configuration.
        
        This method should verify that:
        1. All required fields are present
        2. Field values are within valid ranges
        3. Dependencies are properly specified
        
        Args:
            config: Model configuration to validate
            
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid with detailed message
        """
        pass
```

### 3.2 Model Factory (In Progress)
```python
from typing import Dict, Type
from src.models.base_model import BaseModel
from src.config.base_config import BaseConfig

class ModelFactory:
    """Factory for creating model instances."""
    
    REGISTRY: Dict[str, Type[BaseModel]] = {}
    
    def create_model(self, model_type: str, config: BaseConfig) -> BaseModel:
        """Create a model instance.
        
        Args:
            model_type: Type of model to create
            config: Model configuration
            
        Returns:
            BaseModel: The created model instance
            
        Raises:
            ValueError: If model_type is not supported
            ModelInitializationError: If model initialization fails
        """
        pass

    @classmethod
    def register_model(cls, model_type: str, model_class: Type[BaseModel]) -> None:
        """Register a new model implementation.
        
        Args:
            model_type: Type identifier for the model
            model_class: Model class implementing BaseModel
            
        Raises:
            ValueError: If model_type is already registered
            TypeError: If model_class doesn't implement BaseModel
        """
        pass
```

### 3.3 Output Parser System ✓

#### 3.3.1 Base Output Parser Interface
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pathlib import Path

from ..config.base_config import BaseConfig


class OutputParserError(Exception):
    """Base exception for output parser errors."""
    pass


class OutputParsingError(OutputParserError):
    """Raised when parsing model output fails."""
    pass


class OutputValidationError(OutputParserError):
    """Raised when validation of parsed output fails."""
    pass


class BaseOutputParser(ABC):
    """Base interface for model output parsing.
    
    This interface defines how to parse and structure raw model outputs
    into a standardized format for evaluation and comparison.
    
    Implementations should:
    - Handle different output formats from various models
    - Extract structured field data
    - Normalize field names and values
    - Validate extracted data against expected formats
    """
    
    @abstractmethod
    def initialize(self, config: BaseConfig) -> None:
        """Initialize the parser with configuration.
        
        Args:
            config: Parser configuration
            
        Raises:
            OutputParserError: If initialization fails
            ValueError: If configuration is invalid
        """
        pass
        
    @abstractmethod
    def parse_output(self, model_output: str) -> Dict[str, Any]:
        """Parse raw model output into structured data.
        
        Args:
            model_output: Raw text output from a model
            
        Returns:
            Dict containing extracted field values
            
        Raises:
            OutputParsingError: If parsing fails
        """
        pass
        
    @abstractmethod
    def validate_output(self, parsed_output: Dict[str, Any]) -> bool:
        """Validate the parsed output for completeness and correctness.
        
        Args:
            parsed_output: Dictionary of parsed field values
            
        Returns:
            True if validation passes, False otherwise
        """
        pass
        
    @abstractmethod
    def normalize_output(self, parsed_output: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize field names and values in parsed output.
        
        Applies field-specific normalization to ensure consistent formats
        regardless of the original model output format.
        
        Args:
            parsed_output: Dictionary of parsed field values
            
        Returns:
            Dictionary with normalized field names and values
        """
        pass
```

#### 3.3.2 Output Parser Factory
```python
from typing import Dict, Type, Optional
from src.models.base_output_parser import BaseOutputParser, OutputParserError
from src.config.base_config import BaseConfig


class OutputParserCreationError(Exception):
    """Raised when output parser creation fails."""
    pass


class OutputParserFactory:
    """Factory for creating output parser instances.
    
    Uses registration pattern for adding parser implementations.
    """
    
    # Registry of available parser implementations
    PARSER_REGISTRY: Dict[str, Type[BaseOutputParser]] = {}
    
    def create_parser(
        self, 
        parser_type: str,
        config: Optional[BaseConfig] = None
    ) -> BaseOutputParser:
        """Create and initialize an output parser instance.
        
        Args:
            parser_type: Type of parser to create
            config: Optional explicit configuration
            
        Returns:
            BaseOutputParser: The initialized parser instance
            
        Raises:
            OutputParserCreationError: If parser creation fails
            ValueError: If parser_type is not supported
        """
        pass
        
    @classmethod
    def register_parser(cls, parser_type: str, parser_class: Type[BaseOutputParser]) -> None:
        """Register a new parser implementation.
        
        Args:
            parser_type: Type identifier for the parser
            parser_class: Parser class implementing BaseOutputParser
            
        Raises:
            ValueError: If parser_type is invalid or parser_class doesn't implement BaseOutputParser
        """
        pass
```

#### 3.3.3 Extracted Fields Parser
```python
from typing import Any, Dict, Optional
import re
import json
import logging

from ...base_output_parser import BaseOutputParser, OutputParsingError
from ....config.base_config import BaseConfig
from ....data.validators.extracted_data_validator import ExtractedDataValidator


class ExtractedFieldsOutputParser(BaseOutputParser):
    """Parser for extracting structured fields from model outputs.
    
    This implementation can handle various output formats:
    - Plain text with field names and values
    - JSON-formatted output
    - Key-value pairs in different formats
    
    It normalizes field names to handle variations and validates values.
    """
    
    def __init__(self, data_validator: Optional[ExtractedDataValidator] = None):
        """Initialize with dependencies."""
        pass
        
    def initialize(self, config: BaseConfig) -> None:
        """Initialize with configuration."""
        pass
        
    def parse_output(self, model_output: str) -> Dict[str, Any]:
        """Parse model output text into structured field data."""
        pass
        
    def validate_output(self, parsed_output: Dict[str, Any]) -> bool:
        """Validate parsed output fields."""
        pass
        
    def normalize_output(self, parsed_output: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize field names and values."""
        pass
```

### 3.4 Model Configuration Requirements

#### Required Configuration Fields
```yaml
model:
  name: str  # Unique identifier for the model
  type: str  # Type of model (must match registry)
  version: str  # Model version or checkpoint
  parameters:  # Model-specific parameters
    batch_size: int
    # Other parameters as needed
```

#### Validation Rules
1. All required fields must be present
2. Model type must be registered in factory
3. Version must be valid for model type
4. Parameters must meet model-specific requirements

#### Error Handling
1. Missing fields: Raise ValueError with field name
2. Invalid type: Raise TypeError with expected type
3. Invalid values: Raise ValueError with valid range
4. Resource errors: Raise ModelInitializationError

## 4. Prompt System (In Progress)

### 4.1 Base Prompt Generator Interface
```python
from abc import ABC, abstractmethod
from typing import Dict, Any
from src.config.base_config import BaseConfig

class BasePromptGenerator(ABC):
    """Base interface for prompt generators."""
    
    @abstractmethod
    def initialize(self, config: BaseConfig) -> None:
        """Initialize the prompt generator."""
        pass
    
    @abstractmethod
    def generate_prompt(self, context: Dict[str, Any]) -> str:
        """Generate a prompt from context."""
        pass
```

## 5. Evaluation System (In Progress)

### 5.1 Evaluation Service Interface
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pathlib import Path

class EvaluationService(ABC):
    """Interface for evaluation services."""
    
    @abstractmethod
    def evaluate_model(
        self,
        model: BaseModel,
        test_images: List[Path],
        ground_truth: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate a model's performance."""
        pass
```

## Component Interaction Rules

1. **Configuration Flow**
   - All components must accept configuration through their interfaces
   - Configuration must be validated before use
   - Components must not modify their configuration after initialization

2. **Dependency Injection**
   - All dependencies must be passed explicitly through constructors
   - No global state or singletons
   - Use factory pattern for object creation

3. **Error Handling**
   - Components must define their error conditions
   - Errors must be properly typed and documented
   - Components must clean up resources on error

4. **Testing Requirements**
   - All interfaces must have corresponding test files
   - Tests must verify interface compliance
   - Use mock objects for testing dependencies

## Version History

### v1.0 (Current)
- Completed Configuration System implementation
- Defined base interfaces for Models, Prompts, and Evaluation
- Established component interaction rules

## 6. Data Interfaces ✓

### 6.1 Base Data Loader Interface
```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from PIL import Image
import pandas as pd

class BaseDataLoader(ABC):
    """Base interface for data loading components."""
    
    @abstractmethod
    def __init__(
        self,
        data_dir: Path,
        ground_truth_manager: GroundTruthManager,
        image_dir: Optional[Path] = None,
        cache_enabled: bool = True
    ) -> None:
        """Initialize with required dependencies.
        
        Args:
            data_dir: Path to the root data directory
            ground_truth_manager: Manager for ground truth data handling
            image_dir: Optional path to image directory
            cache_enabled: Whether to enable caching
        """
        pass
        
    @abstractmethod
    def load_ground_truth(self) -> pd.DataFrame:
        """Load the ground truth data from CSV."""
        pass
        
    @abstractmethod
    def load_image(self, invoice_id: str) -> Image.Image:
        """Load an invoice image by its ID."""
        pass
        
    @abstractmethod
    def get_available_invoice_ids(self) -> List[str]:
        """Get a list of all available invoice IDs."""
        pass
        
    @abstractmethod
    def get_invoice_data(self, invoice_id: str) -> Tuple[Image.Image, Dict[str, str]]:
        """Get both the image and ground truth data for an invoice."""
        pass
        
    @abstractmethod
    def clear_cache(self) -> None:
        """Clear any cached data."""
        pass
```

### 6.2 Ground Truth Manager Interface
```python
from pathlib import Path
from typing import List, Dict, Optional

class GroundTruthManager:
    """Interface for ground truth data management."""
    
    def __init__(
        self,
        ground_truth_file: Path,
        required_columns: Optional[List[str]] = None,
        cache_enabled: bool = True
    ) -> None:
        """Initialize the ground truth manager."""
        pass
    
    def validate_ground_truth(self) -> None:
        """Validate ground truth data structure and content."""
        pass
    
    def get_ground_truth(self, invoice_id: str) -> Dict[str, str]:
        """Get ground truth data for a specific invoice."""
        pass
    
    def get_expected_fields(self) -> List[str]:
        """Get list of fields expected to be extracted."""
        pass
```

### 6.3 Data Loader Factory
```python
from pathlib import Path
from typing import Optional, Type, Dict

class DataLoaderFactory:
    """Factory for creating data loader instances."""
    
    REGISTRY: Dict[str, Type[BaseDataLoader]] = {
        "default": DataLoader
    }
    
    @classmethod
    def create_data_loader(
        cls,
        data_dir: Path,
        loader_type: str = "default",
        image_dir: Optional[Path] = None,
        ground_truth_file: Optional[Path] = None,
        cache_enabled: bool = True
    ) -> BaseDataLoader:
        """Create a data loader instance with proper dependency injection."""
        # Create GroundTruthManager first
        ground_truth_file = ground_truth_file or data_dir / "ground_truth.csv"
        ground_truth_manager = GroundTruthManager(
            ground_truth_file=ground_truth_file,
            cache_enabled=cache_enabled
        )
            
        # Create DataLoader with injected dependencies
        loader_class = cls.REGISTRY[loader_type]
        return loader_class(
            data_dir=data_dir,
            ground_truth_manager=ground_truth_manager,
            image_dir=image_dir,
            cache_enabled=cache_enabled
        )
```

### 6.4 Custom Exceptions
```python
class DataLoadError(Exception):
    """Base exception for data loading errors."""
    pass

class GroundTruthError(DataLoadError):
    """Raised when there is an error with ground truth data."""
    pass

class ImageLoadError(DataLoadError):
    """Raised when there is an error loading an image."""
    pass

class DataValidationError(DataLoadError):
    """Raised when data validation fails."""
    pass
```

### 6.5 Ground Truth Field Specifications

#### Field Types and Validation
```python
class GroundTruthFields:
    """Specification for ground truth data fields."""
    
    TOTAL_AMOUNT = {
        "type": float,
        "validation": "Positive number with 2 decimal places",
        "storage": "Float",
        "example": "123.45"
    }
    
    WORK_ORDER = {
        "type": str,
        "validation": "Alphanumeric, preserves leading zeros",
        "storage": "Object (string)",
        "example": "00123"
    }
```

#### Comparison Strategy
```python
class FieldComparison:
    """Strategy for comparing LLM outputs with ground truth."""
    
    @staticmethod
    def compare_total(ground_truth: float, llm_output: str) -> bool:
        """Compare total amount values.
        
        Ground Truth: Float with 2 decimal places
        LLM Output: Various string formats ("$123.45", "123", etc.)
        Strategy: Normalize to float, compare with epsilon
        """
        pass
    
    @staticmethod
    def compare_work_order(ground_truth: str, llm_output: str) -> bool:
        """Compare work order numbers.
        
        Ground Truth: String preserving exact format
        LLM Output: Potentially different format
        Strategy: Case-insensitive exact match after normalization
        """
        pass
```

See ADR-001 for detailed rationale and implementation guidelines.

## 7. Interface Interactions

### 7.1 Configuration Flow

1. `ConfigLoader` loads YAML files
2. `ConfigFactory` creates appropriate configuration objects
3. Configuration objects are validated
4. Validated configurations are passed to components

### 7.2 Model Processing Flow

1. `DataLoader` loads input images and ground truth
2. `BaseModel` processes images using configuration
3. `BasePromptGenerator` generates prompts based on context
4. `EvaluationService` evaluates results against ground truth

## 8. Error Handling

### 8.1 Custom Exceptions

```python
class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass

class ConfigLoadError(Exception):
    """Raised when configuration loading fails."""
    pass

class ModelInitializationError(Exception):
    """Raised when model initialization fails."""
    pass

class ModelProcessingError(Exception):
    """Raised when model processing fails."""
    pass
```

## 9. Version Control

This document should be updated whenever:
- New interfaces are added
- Existing interfaces are modified
- Interface interactions change
- Error handling is updated

## 10. References

- [Project Directory Structure](../project_planning/project-directory.md)
- [Core Architectural Principles](../project_planning/core-architectural-principals.mdc)
- [Development Guidelines](../project_planning/development-guidelines.md)

## 11. Testing Guidelines

### 11.1 Test Structure
- One test file per component
- Shared fixtures in conftest.py
- Test data in fixtures directory
- Clear test naming conventions

### 11.2 Test Coverage
- Minimum 80% coverage required
- Critical paths must be tested
- Edge cases must be covered
- Error conditions must be tested

### 11.3 Test Fixtures
```python
@pytest.fixture
def temp_config_dir() -> Path:
    """Create temporary directory for test configuration files."""
    pass

@pytest.fixture
def config_factory() -> ConfigFactory:
    """Create ConfigFactory instance for testing."""
    pass

@pytest.fixture
def config_loader(temp_config_dir: Path, config_factory: ConfigFactory) -> ConfigLoader:
    """Create ConfigLoader instance for testing."""
    pass
```

### 11.4 Test Data
- Use realistic test data
- Include both valid and invalid cases
- Document test data structure
- Keep test data minimal but complete

## 12. Configuration Guidelines

### 12.1 YAML Structure
- Clear hierarchy
- Consistent naming
- Documented fields
- Type specifications

### 12.2 Validation Rules
- Required fields
- Field types
- Value ranges
- Dependencies

### 12.3 Error Messages
- Clear and specific
- Include context
- Suggest solutions
- Use consistent format

### 12.4 Example Configuration Files
```yaml
# config/models/model_config.yaml
model:
  name: test_model
  type: test_type
  parameters:
    param1: value1
    param2: value2

# config/prompts/prompt_config.yaml
prompt:
  type: test_type
  template: test_template
  parameters:
    param1: value1
    param2: value2

# config/evaluation.yaml
evaluation:
  metrics:
    - metric1
    - metric2
  dataset:
    path: test_path
  output:
    format: json
```

## 13. Dependency Injection Patterns ✓

### 13.1 Core Principles
1. **Constructor Injection**
   - Dependencies must be passed through constructors
   - No service locator or global state
   - Clear dependency declaration in interfaces
   - Example:
     ```python
     def __init__(
         self,
         config_factory: ConfigFactory,
         data_loader: BaseDataLoader,
         model: BaseModel
     ) -> None:
         self.config_factory = config_factory
         self.data_loader = data_loader
         self.model = model
     ```

2. **Factory Pattern**
   - Factories handle dependency creation
   - Factories manage object lifecycles
   - Dependencies created in correct order
   - Example:
     ```python
     class ServiceFactory:
         def create_service(self) -> BaseService:
             config = self.create_config()
             data_loader = self.create_data_loader(config)
             model = self.create_model(config)
             return Service(config, data_loader, model)
     ```

3. **Interface Dependencies**
   - Depend on interfaces, not implementations
   - Use abstract base classes
   - Clear interface contracts
   - Example:
     ```python
     class Service:
         def __init__(self, data_loader: BaseDataLoader):
             # Depends on interface, not concrete class
             self._data_loader = data_loader
     ```

4. **Configuration Injection**
   - Configuration passed as dependencies
   - No direct loading of config files
   - Use configuration objects
   - Example:
     ```python
     class Model:
         def __init__(self, config: BaseConfig):
             self.config = config
             self.parameters = config.get_data()
     ```

### 13.2 Implementation Guidelines
1. **Component Creation**
   - Use factories for complex objects
   - Inject all dependencies
   - Clear creation order
   - Example from DataLoader:
     ```python
     # Factory creates and injects dependencies
     loader = factory.create_data_loader(
         data_dir=Path("data/"),
         image_dir=Path("data/images"),
         ground_truth_file=Path("data/ground_truth.csv")
     )
     ```

2. **Testing Support**
   - Easy dependency mocking
   - Clear test setup
   - Isolated component testing
   - Example:
     ```python
     def test_service(mock_data_loader, mock_model):
         service = Service(
             data_loader=mock_data_loader,
             model=mock_model
         )
         assert service.process() == expected_result
     ```

3. **Error Handling**
   - Clear dependency validation
   - Proper error propagation
   - Descriptive error messages
   - Example:
     ```python
     def __init__(self, config: BaseConfig):
         if not isinstance(config, BaseConfig):
             raise TypeError("config must implement BaseConfig")
         self.config = config
     ```

4. **Documentation**
   - Document dependencies
   - Clear initialization requirements
   - Usage examples
   - Example:
     ```python
     class Service:
         """Service requiring data_loader and model dependencies.
         
         Args:
             data_loader: Handles data loading operations
             model: Processes the loaded data
         
         Example:
             loader = DataLoader(...)
             model = Model(...)
             service = Service(loader, model)
         """
     ``` 