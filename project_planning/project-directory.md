# Project Directory Structure: LMM Invoice Data Extraction Comparison

```
invoice-extraction-comparison/
├── README.md                        # Project overview and setup instructions
├── requirements.txt                 # Python dependencies
├── pytest.ini                       # pytest configuration
│
├── config/                          # Configuration files
│   ├── models/                      # Model-specific configurations
│   │   ├── pixtral.yaml             # Pixtral-12B model configuration
│   │   ├── llama_vision.yaml        # Llama-3.2-11B-Vision model configuration
│   │   └── doctr.yaml               # Doctr model configuration
│   ├── prompts/                     # Prompt template configurations
│   │   ├── basic.yaml               # Basic prompt configuration
│   │   ├── detailed.yaml            # Detailed prompt configuration
│   │   ├── few_shot.yaml            # Few-shot prompt configuration
│   │   ├── step_by_step.yaml        # Step-by-step prompt configuration
│   │   └── locational.yaml          # Locational prompt configuration
│   └── evaluation.yaml              # Evaluation configuration
│
├── models/                          # Model weights and cache (gitignored)
│   ├── README.md                    # Directory documentation
│   ├── pixtral/                     # Pixtral-12B model files
│   ├── llama_vision/                # Llama Vision model files
│   └── doctr/                       # DocTR model files
│
├── data/                            # Data storage (gitignored)
│   ├── raw/                         # Original invoice images and ground truth
│   │   ├── images/                  # Invoice images (e.g., 12147.jpg)
│   │   └── ground_truth.csv         # Ground truth CSV file
│   └── processed/                   # Any preprocessed data (if needed)
│
├── src/                             # Source code
│   ├── __init__.py
│   │
│   ├── config/                      # Configuration management
│   │   ├── __init__.py              # Exports public interfaces
│   │   ├── base_config.py           # Abstract base class for configs
│   │   ├── config_loader.py         # Configuration loading service
│   │   ├── config_factory.py        # Factory for config objects
│   │   ├── config_parser.py         # Protocol for config parsing
│   │   └── implementations/         # Concrete implementations
│   │       ├── __init__.py          # Implementation exports
│   │       ├── model_config.py      # Model configuration
│   │       ├── prompt_config.py     # Prompt configuration
│   │       └── evaluation_config.py # Evaluation configuration
│   │
│   ├── validation/                  # Validation utilities
│   │   ├── __init__.py              # Exports public interfaces
│   │   ├── validation_result.py     # Validation result class
│   │   ├── model_config_validator.py # Model config validator interface
│   │   └── implementations/         # Concrete implementations
│   │       ├── __init__.py          # Implementation exports
│   │       └── basic_model_validator.py # Basic model validator
│   │
│   ├── data/                        # Data management
│   │   ├── __init__.py              # Exports public interfaces
│   │   ├── base_data_loader.py      # Abstract base class for data loading
│   │   ├── data_loader_factory.py   # Factory for data loader objects
│   │   ├── ground_truth_manager.py  # Ground truth handling
│   │   └── implementations/         # Concrete implementations
│   │       ├── __init__.py          # Implementation exports
│   │       └── csv_data_loader.py   # CSV-based data loader
│   │
│   ├── models/                      # Model implementations
│   │   ├── __init__.py
│   │   ├── model_factory.py         # Factory for creating models
│   │   ├── base_model.py            # Abstract base class for all models
│   │   ├── base_output_parser.py    # Abstract base class for output parsers
│   │   ├── output_parser_factory.py # Factory for creating output parsers
│   │   ├── output_parser.py         # Parser registration module
│   │   └── implementations/         # Specific model implementations
│   │       ├── __init__.py
│   │       ├── pixtral_model.py     # Pixtral-12B model implementation
│   │       ├── llama_vision_model.py # Llama-3.2-11B-Vision model implementation
│   │       └── doctr_model.py       # Doctr model implementation
│   │
│   ├── prompts/                     # Prompt management
│   │   ├── __init__.py
│   │   ├── prompt_factory.py        # Factory for creating prompt generators
│   │   ├── base_prompt_generator.py # Base class for prompt generators
│   │   ├── prompt_formatter.py      # Format prompts for models
│   │   └── strategies/              # Prompt strategy implementations
│   │       ├── __init__.py
│   │       ├── basic_prompt.py      # Basic prompt implementation
│   │       ├── detailed_prompt.py   # Detailed prompt implementation
│   │       ├── few_shot_prompt.py   # Few-shot prompt implementation
│   │       ├── step_by_step_prompt.py # Step-by-step prompt implementation
│   │       └── locational_prompt.py # Locational prompt implementation
│   │
│   ├── evaluation/                  # Evaluation framework
│   │   ├── __init__.py
│   │   ├── evaluation_service.py    # Evaluation orchestration
│   │   ├── metrics_calculator.py    # Calculate evaluation metrics
│   │   └── results_manager.py       # Store and retrieve results
│   │
│   └── visualization/               # Visualization utilities
│       ├── __init__.py
│       ├── visualization_service.py # Visualization orchestration
│       ├── comparison_plotter.py    # Generate comparison plots
│       └── results_table.py         # Generate result tables
│
├── tests/                           # Test suite
│   ├── __init__.py
│   ├── conftest.py                  # pytest fixtures and configuration
│   ├── test_config.py               # Configuration system tests
│   └── fixtures/                    # Test data and configurations
│       └── config/                  # Configuration test fixtures
│           ├── models/              # Model config test files
│           │   ├── valid_model.yaml # Valid model configuration
│           │   └── invalid_model.yaml # Invalid model configuration
│           ├── prompts/             # Prompt config test files
│           │   ├── valid_prompt.yaml # Valid prompt configuration
│           │   └── invalid_prompt.yaml # Invalid prompt configuration
│           └── evaluation.yaml      # Evaluation config test file
│
├── notebooks/                       # Jupyter notebooks
│   ├── experiment_template.ipynb    # Template for experiment notebooks
│   ├── model_experiments/           # Individual model experiment notebooks
│   │   ├── pixtral_basic.ipynb      # Pixtral-12B with basic prompt
│   │   ├── pixtral_detailed.ipynb   # Pixtral-12B with detailed prompt
│   │   ├── llama_vision_basic.ipynb # Llama-3.2-11B-Vision with basic prompt
│   │   ├── llama_vision_detailed.ipynb # Llama-3.2-11B-Vision with detailed prompt
│   │   ├── doctr_basic.ipynb        # Doctr with basic prompt
│   │   ├── doctr_detailed.ipynb     # Doctr with detailed prompt
│   │   └── ...                      # Other model/prompt combinations
│   └── results_analysis.ipynb       # Results aggregation and visualization
│
├── results/                         # Evaluation results (gitignored)
│   └── experiments/                 # Individual experiment results
│       ├── llava_basic_4bit.json    # Example result file
│       ├── llava_detailed_4bit.json # Example result file
│       └── ...
│
└── docs/                            # Documentation
    ├── project_overview.md          # Project overview and plan
    ├── project_rules.md             # Development rules and guidelines
    ├── project_todo.md              # Implementation tasks and schedule
    └── architecture.md              # System architecture documentation
```

## Key Directory Relationships

### Configuration Management (`src/config/`) ✓
- Completed interface-based design with `BaseConfig` abstract class
- Implemented factory pattern with `ConfigFactory`
- Added `ConfigParser` protocol and `YAMLConfigParser` implementation
- Clear separation between interface and implementations
- YAML configuration files in `config/` directory
- All configuration is external to code
- Comprehensive test coverage (97%)
- Example usage:
  ```python
  from pathlib import Path
  from src.config import ConfigLoader, ConfigFactory, YAMLConfigParser
  from src.config.base_config import BaseConfig
  
  # Create dependencies
  factory = ConfigFactory()
  parser = YAMLConfigParser()  # Or use default YAML parser
  
  # Initialize with proper dependency injection
  loader = ConfigLoader(
      config_path=Path("config/"),
      config_factory=factory,
      config_parser=parser  # Optional, defaults to YAMLConfigParser
  )
  
  # Load configurations
  model_config = loader.load_model_config("pixtral")
  prompt_config = loader.load_prompt_config("basic")
  eval_config = loader.load_evaluation_config()
  
  # Access configuration data
  model_name = model_config.get_data()["name"]
  model_type = model_config.get_data()["type"]
  model_params = model_config.get_data()["parameters"]
  ```

### Test Suite (`tests/`) - Configuration Section ✓
- Comprehensive test coverage for configuration system
- Mock parsers for testing
- Fixtures for configuration testing
- Example test structure:
  ```python
  class MockConfigParser:
      """Mock configuration parser for testing."""
      def load(self, file_path: Path) -> Dict[str, Any]:
          if not file_path.exists():
              raise FileNotFoundError(f"Configuration file not found: {file_path}")
          return {
              "model": {
                  "name": "test_model",
                  "type": "mock",
                  "parameters": {"mock_param": "value"}
              }
          }
  
  def test_config_loader_with_mock(config_path):
      """Test loading with mock parser."""
      factory = ConfigFactory()
      parser = MockConfigParser()
      loader = ConfigLoader(config_path, factory, parser)
      
      config = loader.load_model_config("test_model")
      assert isinstance(config, BaseConfig)
      assert config.get_data()["name"] == "test_model"
  ```

### Data Management (`src/data/`) ✓
- Clear separation between raw and processed data
- Ground truth CSV paired with invoice images
- All data files are gitignored
- Completed interface-based design with `BaseDataLoader` abstract class
- Implemented factory pattern with `DataLoaderFactory`
- Added custom exceptions for error handling
- Clear separation between interface and implementations
- Comprehensive error handling and logging
- Field-specific data type handling:
  - Total Amount: Stored as float, cleaned during load
  - Work Order Number: Preserved as string with format
- Robust validation and comparison strategies
- Completed verification notebook for data pipeline testing
- Confirmed data loading with 29 invoice samples
- Phase 1 implementation fully completed
- Example usage:
  ```python
  from pathlib import Path
  from src.data import DataLoaderFactory, GroundTruthManager
  
  # Create data loader instance using factory
  factory = DataLoaderFactory()
  loader = factory.create_data_loader(
      data_dir=Path("data/"),
      image_dir=Path("data/images"),
      ground_truth_file=Path("data/ground_truth.csv"),
      cache_enabled=True
  )
  
  # Get available invoice IDs
  invoice_ids = loader.get_available_invoice_ids()
  
  # Load specific invoice data with proper type handling
  image, ground_truth = loader.get_invoice_data("1017")
  
  # Access normalized ground truth data
  work_order = ground_truth["Work Order Number"]  # Preserves format
  total_cost = ground_truth["Total"]  # Cleaned and normalized
  ```

### Source Code (`src/`)
- Organized by component responsibility
- Clear separation between interfaces and implementations
- Each directory contains related functionality
- Implementation details hidden behind interfaces

### Notebooks (`notebooks/`)
- Template notebook for consistency
- Organized model experiments
- Separate analysis notebook

### Results (`results/`)
- Standardized result format
- One file per experiment
- All result files are gitignored

## Import Relationships

### Core Import Patterns

```python
# Typical notebook imports
from pathlib import Path
from src.config import ConfigLoader, ConfigFactory, YAMLConfigParser
from src.config.base_config import BaseConfig
from src.models import ModelFactory
from src.prompts import PromptFactory
from src.evaluation import EvaluationService
from src.data import DataLoader

# Typical component imports
from src.config.implementations.model_config import ModelConfig
from src.models.base_model import BaseModel
from src.prompts.base_prompt_generator import BasePromptGenerator
```

### Test Import Patterns

```python
# Test imports
from typing import Dict, Any
from pathlib import Path
from src.config.config_loader import ConfigLoader
from src.config.config_factory import ConfigFactory
from src.config.base_config import BaseConfig
from src.config.implementations.model_config import ModelConfig
from src.config.implementations.prompt_config import PromptConfig
from src.config.implementations.evaluation_config import EvaluationConfig
```

### Dependency Flow

1. Configuration loaded first
2. Configuration passed to components
3. Components interact through well-defined interfaces
4. Results flow from components to storage

## File Purpose Quick Reference

### Configuration System (Completed) ✓
- `base_config.py`: Interface all configs must implement
- `config_factory.py`: Creates config objects based on type
- `config_loader.py`: Loads and validates configuration files with dependency injection
- `model_config.py`: Model-specific configuration implementation
- `prompt_config.py`: Prompt-specific configuration implementation
- `evaluation_config.py`: Evaluation-specific configuration implementation

### Output Parser System (Completed) ✓
- `base_output_parser.py`: Interface all output parsers must implement
- `output_parser_factory.py`: Creates parser instances based on configuration
- `output_parser.py`: Handles registration of parsers
- `extracted_fields_parser.py`: Main parser implementation for extracting structured data

### Other Components (In Progress)
- `model_factory.py`: Creates model instances based on configuration
- `base_model.py`: Defines the interface all models must implement
- `prompt_factory.py`: Creates prompt generators based on configuration
- `evaluation_service.py`: Orchestrates the evaluation process
- `results_manager.py`: Handles saving and loading of results
- `experiment_template.ipynb`: Template for creating experiment notebooks
- `results_analysis.ipynb`: Aggregates and visualizes experiment results
- `test_config.py`: Tests for configuration system
- `conftest.py`: Shared test fixtures and configuration

### Model Management
- Model weights and cache files in `models/`
- Model implementations in `src/models/`
- Model configurations in `config/models/`
- Clear separation between code, weights, and configuration

### Output Parser Management
- Parser interfaces in `src/models/`
- Parser implementations in `src/models/output_parser/implementations/`
- Parser factory provides consistent creation pattern
- High test coverage (85-100% across components)