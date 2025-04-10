# LMM Invoice Data Extraction Comparison

A comprehensive comparison of Large Multimodal Models (LMMs) for invoice data extraction, focusing on accuracy, efficiency, and practical implementation.

## Project Overview

This project compares three LMMs (Pixtral-12B, Llama-3.2-11B-Vision, and Doctr) for invoice data extraction using five different prompt strategies. The goal is to provide a detailed analysis of model performance across different prompt types and identify optimal configurations for invoice data extraction.

## System Requirements

### Hardware Requirements
- NVIDIA GPU with at least 93GB memory (H100 NVL recommended)
- 16GB RAM minimum
- 50GB free disk space for code, data, and model weights

### Software Requirements
- Python 3.13.2 or higher
- CUDA 11.8 (required for PyTorch)
- CUDA-compatible GPU drivers

### Development Environment
- VS Code with Python extension recommended
- Pre-commit hooks for code quality
- Virtual environment for dependency isolation

## Dependencies

Core dependencies include:
- PyTorch 2.1.0+cu118
- Transformers 4.50.3
- Pillow 9.3.0
- PyYAML 6.0.1
- Pandas 2.2.3
- NumPy 1.24.1

Development tools:
- pytest 8.3.5 with coverage and mock support
- black 24.1.1 for formatting
- flake8 7.0.0 for linting
- mypy 1.8.0 for type checking

For a complete list, see `requirements.txt`.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/invoice-extraction-comparison.git
cd invoice-extraction-comparison
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Unix:
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download model weights:
   - Each model's weights should be placed in its respective directory under `models/`:
     - Pixtral-12B: `models/pixtral/`
     - Llama Vision: `models/llama_vision/`
     - DocTR: `models/doctr/`
   - Model weights are not included in the repository
   - See each model's documentation for download instructions

5. Verify installation:
```python
import torch
import yaml
from pathlib import Path
from src.config import ConfigLoader, ConfigFactory

# Check CUDA
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")

# Test configuration system
factory = ConfigFactory()
loader = ConfigLoader(
    config_path=Path("config/"),
    config_factory=factory
)
```

## Project Structure

```
invoice-extraction-comparison/
├── README.md                        # Project overview and setup instructions
├── requirements.txt                 # Python dependencies
├── pytest.ini                      # pytest configuration
│
├── config/                         # Configuration files ✓
│   ├── models/                     # Model-specific configurations
│   ├── prompts/                    # Prompt configurations
│   └── evaluation.yaml             # Evaluation parameters
│
├── models/                         # Model weights and cache (gitignored)
│   ├── README.md                  # Directory documentation
│   ├── pixtral/                  # Pixtral-12B model files
│   ├── llama_vision/             # Llama Vision model files
│   └── doctr/                    # DocTR model files
│
├── data/                          # Data storage (gitignored)
│   ├── raw/                       # Original invoice images
│   └── processed/                 # Preprocessed data
│
├── src/                           # Source code
│   ├── config/                    # Configuration system ✓
│   │   ├── base_config.py        # Configuration interface
│   │   ├── config_factory.py     # Factory implementation
│   │   ├── implementations/      # Concrete config implementations
│   ├── data/                     # Data handling ✓
│   │   ├── base_data_loader.py   # Data loader interface
│   │   ├── data_loader_factory.py # Factory implementation
│   │   ├── implementations/      # Concrete loaders
│   ├── models/                   # Model implementations
│   │   ├── base_model.py        # Base interface ✓
│   │   ├── model_factory.py     # Factory ✓
│   │   └── implementations/     # Model implementations (Planned)
│   ├── prompts/                  # Prompt management ✓
│   │   ├── base_prompt_generator.py  # Generator interface ✓
│   │   ├── prompt_factory.py     # Factory (In Progress)
│   │   ├── prompt_config.py      # Configuration ✓
│   │   └── implementations/      # Concrete generators
│   │       └── basic_prompt_generator.py  # Basic implementation ✓
│   ├── evaluation/              # Evaluation framework (In Progress)
│   └── visualization/          # Visualization utilities (In Progress)
│
├── tests/                      # Test suite
│   ├── test_config.py         # Configuration tests (97% coverage) ✓
│   ├── test_base_model.py     # Model interface tests (83% coverage) ✓
│   ├── test_model_factory.py  # Factory tests (95% coverage) ✓
│   └── fixtures/              # Test data
│
├── notebooks/                  # Jupyter notebooks
└── docs/                      # Documentation
    ├── adr/                   # Architecture Decision Records
    │   ├── 001-ground-truth-data-types.md
    │   ├── 002-image-processor-configuration.md
    │   ├── 003-dependency-injection-patterns.md
    │   └── 004-model-factory-registration.md
    └── interface_control_document.md  # Interface specifications ✓
```

## Architectural Principles

The project follows strict architectural principles:

### 1. Separation of Concerns
- Each component has a single responsibility
- Clear boundaries between system parts 
- Interfaces separate from implementations

### 2. Interface-Based Design
- Abstract base classes define interfaces
- Factory pattern for object creation
- Example:
  ```python
  # Interface definition
  class BaseModel(ABC):
      @abstractmethod
      def process_image(self, image_path: Path) -> Dict[str, Any]:
          """Process an image and return structured data."""
          pass
  
  # Factory implementation
  class ModelFactory:
      REGISTRY: Dict[str, Type[BaseModel]] = {}
      
      @classmethod
      def register_model(cls, name: str, model_class: Type[BaseModel]) -> None:
          """Register a model implementation."""
          cls.REGISTRY[name] = model_class
      
      def create_model(self, name: str, config: BaseConfig) -> BaseModel:
          """Create a model instance by name."""
          if name not in self.REGISTRY:
              raise ValueError(f"Unknown model: {name}")
          model = self.REGISTRY[name]()
          model.initialize(config)
          return model
  ```

### 3. Dependency Injection
- Dependencies explicitly passed to constructors
- No global state or singletons
- Example:
  ```python
  # Constructor-based injection
  class Service:
      def __init__(
          self,
          data_loader: BaseDataLoader,
          model: BaseModel,
          config: BaseConfig
      ):
          self.data_loader = data_loader
          self.model = model
          self.config = config
  ```

### 4. Error Handling
- Domain-specific exception hierarchy
- Early input validation
- Detailed error messages
- Example:
  ```python
  # Exception hierarchy
  class ModelError(Exception):
      """Base exception for model errors."""
      pass
      
  class ModelInitializationError(ModelError):
      """Error during model initialization."""
      pass
      
  # Validation with specific errors
  def process_image(image_path: Path) -> Dict[str, Any]:
      if not isinstance(image_path, Path):
          raise TypeError("Image path must be a Path object")
      if not image_path.exists():
          raise FileNotFoundError(f"Image not found: {image_path}")
      # Process the image...
  ```

## Configuration System ✓

The project uses a robust, interface-based configuration system with dependency injection:

1. **Base Configuration Interface**:
   - Abstract base class for all configurations
   - Type-safe data access methods
   - Standardized validation
   - No global state or singletons

2. **Configuration Manager**:
   - Interface-based design with proper DI
   - Constructor-based dependency injection
   - Type-safe configuration handling
   - Proper separation of type definitions

3. **Configuration Factory**:
   - Creates typed configuration objects
   - Implements factory pattern
   - Supports registration of new types
   - Type-safe configuration creation

4. **Type System**:
   - Clear separation of type definitions
   - Avoids circular dependencies
   - Enum-based type definitions
   - Proper module organization

Example usage:
```python
from pathlib import Path
from src.config import ConfigManager, ConfigFactory, ConfigType

# Create dependencies
factory = ConfigFactory()

# Initialize with dependency injection
config_manager = ConfigManager(
    config_root="config/",
    config_factory=factory
)

# Load configurations
model_config = config_manager.get_config(ConfigType.MODEL, "pixtral")
prompt_config = config_manager.get_config(ConfigType.PROMPT, "basic")
eval_config = config_manager.get_config(ConfigType.EVALUATION, "default")

# Access configuration data
model_name = model_config.get_data()["name"]
model_type = model_config.get_data()["type"]
model_params = model_config.get_data()["parameters"]
```

## Model Management ✓

The project separates model-related files into three distinct areas:

1. **Model Weights** (`models/`):
   - Downloaded model weights and checkpoints
   - Model-specific cache files
   - Not tracked in git
   - Organized by model name

2. **Model Code** (`src/models/`):
   - Model implementations based on BaseModel interface ✓
   - Factory for model creation ✓ 
   - Interface definitions and abstractions ✓
   - Common utilities and error handling ✓
   - Output parsing system ✓
   - Example usage:
   ```python
   from pathlib import Path
   from src.models import ModelFactory, create_parser
   from src.config import ConfigLoader, ConfigFactory
   
   # Register model implementations
   from src.models.implementations.pixtral_model import PixtralModel
   ModelFactory.register_model("pixtral", PixtralModel)
   
   # Create model via factory
   config_loader = ConfigLoader(
       config_path=Path("config/"), 
       config_factory=ConfigFactory()
   )
   model_config = config_loader.load_model_config("pixtral")
   
   # Factory uses dependency injection and dynamic registration
   factory = ModelFactory()
   model = factory.create_model("pixtral", model_config)
   
   # Process an image
   raw_output = model.process_image(Path("data/invoice.jpg"))
   
   # Parse and normalize output
   parser = create_parser("default")
   parsed_output = parser.parse_output(raw_output)
   normalized_output = parser.normalize_output(parsed_output)
   
   # Validate the output
   is_valid = parser.validate_output(normalized_output)
   ```

3. **Model Configuration** (`config/models/`):
   - Model parameters
   - Architecture settings
   - Training configurations
   - Inference settings
   - Example configuration:
   ```yaml
   model:
     name: "pixtral"
     type: "pixtral"
     version: "1.0"
     parameters:
       batch_size: 1
       # Other model-specific parameters...
   ```

## Data Management ✓

The project uses a robust data management system with proper dependency injection:

1. **Data Loader**:
   - Interface-based design with dependency injection
   - Factory pattern for object creation
   - Clear separation of responsibilities
   - Example usage:
   ```python
   from pathlib import Path
   from src.data import DataLoaderFactory
   
   # Create data loader using factory (handles dependency injection)
   factory = DataLoaderFactory()
   loader = factory.create_data_loader(
       data_dir=Path("data/"),
       image_dir=Path("data/images"),
       ground_truth_file=Path("data/ground_truth.csv"),
       cache_enabled=True
   )
   
   # Access data with proper type handling
   invoice_ids = loader.get_available_invoice_ids()
   image, ground_truth = loader.get_invoice_data("1017")
   
   # Access normalized fields with proper types
   work_order = ground_truth["Work Order Number"]  # Format preserved
   total_cost = ground_truth["Total"]  # Cleaned and normalized
   ```

2. **Ground Truth Manager**:
   - Handles data validation and type conversion
   - Injected into DataLoader
   - Manages data caching
   - Example usage:
   ```python
   from src.data import GroundTruthManager
   
   # Create manager (usually done by factory)
   manager = GroundTruthManager(
       ground_truth_file=Path("data/ground_truth.csv"),
       cache_enabled=True
   )
   
   # Validate and access data
   manager.validate_ground_truth()
   data = manager.get_ground_truth("1017")
   ```

## Testing

The project uses pytest with comprehensive coverage and proper test isolation:

1. **Test Organization**:
   ```
   tests/
     test_base_model.py         # Interface tests
     test_model_factory.py      # Factory tests 
     test_implementations/      # Implementation tests
   ```

2. **Fixture Management**:
   ```python
   # Reset global state before/after tests
   @pytest.fixture(autouse=True)
   def reset_registry():
       """Clear registry before and after tests."""
       ModelFactory.MODEL_REGISTRY.clear()
       yield
       ModelFactory.MODEL_REGISTRY.clear()
   
   # Mock dependencies
   @pytest.fixture
   def mock_config_manager():
       """Create mock config manager."""
       return Mock(spec=ConfigManager)
   
   # Component under test
   @pytest.fixture
   def factory(mock_config_manager):
       """Create factory with mock dependencies."""
       return ModelFactory(config_manager=mock_config_manager)
   ```

3. **Run all tests**:
```bash
pytest tests/ -v
```

4. **Run with coverage**:
```bash
pytest tests/ -v --cov=src
```

5. **Run specific test file**:
```bash
pytest tests/test_model_factory.py -v
```

Current test coverage:
- Configuration System: 97% coverage ✓
- BaseModel Interface: 83% coverage ✓
- ModelFactory: 95% coverage ✓
- OutputParser System: 85-90% coverage ✓
- DataLoader: 94% coverage ✓
- GroundTruthManager: 96% coverage ✓

## Development Guidelines

1. **Code Quality**:
   - Use black for formatting
   - Use flake8 for linting
   - Use mypy for type checking
   - Follow PEP 8 style guide

2. **Testing Requirements**:
   - Write tests for all new code
   - Maintain >80% coverage
   - Include edge cases
   - Use appropriate fixtures
   - Ensure test isolation 
   - Mock dependencies properly
   - Reset global state

3. **Documentation**:
   - Update ICD for interface changes
   - Create ADRs for significant decisions
   - Document all public APIs
   - Include usage examples
   - Keep README current

4. **Error Handling**:
   - Use domain-specific exceptions
   - Validate input early
   - Provide detailed error messages
   - Clean up resources in case of errors
   - Test error conditions

5. **Git Workflow**:
   - Create feature branches
   - Write clear commit messages
   - Update tests with changes
   - Request reviews for PRs

## Architecture Decision Records (ADRs)

The project uses ADRs to document significant architectural decisions:

1. **ADR-001: Ground Truth Data Types**
   - Decisions regarding data type handling for invoice fields
   - Format preservation vs. normalization tradeoffs

2. **ADR-003: Dependency Injection Patterns**
   - Standardization of DI across the codebase
   - Constructor injection as primary pattern
   - Factory pattern integration

3. **ADR-004: Model Factory Registration Pattern**
   - Dynamic registration for model implementations
   - Decoupling factory from concrete implementations
   - Testing strategy for factories

4. **ADR-007: Prompt Generation System Design**
   - Flexible prompt generation system with multiple strategies
   - Base components, template management, and prompt strategies
   - Comprehensive test coverage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

[Your chosen license]

## Acknowledgments

- Original dataset providers
- Model developers and maintainers
- Open-source community contributors

## Prompt Generation System ✓

The project implements a flexible prompt generation system with multiple strategies:

1. **Base Components**:
   - `BasePromptGenerator` interface defines standard prompt generation contract ✓
   - `PromptConfig` manages template configuration and validation ✓
   - Factory pattern with proper test isolation ✓
   - Template caching for performance optimization (Planned)

2. **Template Management**:
   ```python
   class PromptTemplate:
       name: str
       text: str
       category: str
       field_to_extract: str
       description: str
       version: Optional[str]
       format_instructions: Optional[str]
       metadata: Optional[Dict[str, Any]]
   ```

3. **Prompt Strategies**:
   - Basic: Direct field extraction prompts ✓
   - Detailed: Comprehensive instruction prompts (Planned)
   - Few-Shot: Example-based prompts (Planned)
   - Step-by-Step: Guided extraction prompts (Planned)
   - Locational: Spatial-aware prompts (Planned)

4. **Implementation Example**:
   ```python
   # Create prompt generator with proper validation
   generator = prompt_factory.create_generator("basic", "work_order")
   generator.initialize(prompt_config)
   
   # Generate prompt with field-specific validation
   context = {"field_type": "work_order"}
   prompt = generator.generate_prompt(context)
   ```

5. **Key Features**:
   - Field-specific format validation ✓
   - Template validation ✓
   - Robust error handling ✓
   - Resource cleanup management ✓
   - Proper test isolation ✓
   - Comprehensive test coverage (96%) ✓

For detailed design decisions, see ADR-007: Prompt Generation System Design.
