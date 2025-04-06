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
│   ├── data/                     # Data handling ✓
│   ├── models/                   # Model implementations (In Progress)
│   ├── prompts/                  # Prompt management (In Progress)
│   ├── evaluation/              # Evaluation framework (In Progress)
│   └── visualization/          # Visualization utilities (In Progress)
│
├── tests/                      # Test suite
│   ├── test_config.py         # Configuration tests (97% coverage) ✓
│   └── fixtures/              # Test data
│
├── notebooks/                  # Jupyter notebooks
└── docs/                      # Documentation
```

## Configuration System ✓

The project uses a robust, interface-based configuration system with dependency injection:

1. **Base Configuration Interface**:
   - Abstract base class for all configurations
   - Type-safe data access methods
   - Standardized validation

2. **Configuration Parser Protocol**:
   - Flexible parsing strategy
   - YAML parsing by default
   - Extensible for other formats

3. **Configuration Factory**:
   - Creates typed configuration objects
   - Implements factory pattern
   - Supports registration of new types

4. **Configuration Loader**:
   - Dependency injection based design
   - Path-based configuration loading
   - Comprehensive error handling

Example usage:
```python
from pathlib import Path
from src.config import ConfigLoader, ConfigFactory, YAMLConfigParser

# Create dependencies
factory = ConfigFactory()
parser = YAMLConfigParser()  # Optional, uses default if not specified

# Initialize with dependency injection
loader = ConfigLoader(
    config_path=Path("config/"),
    config_factory=factory,
    config_parser=parser  # Optional
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

## Model Management

The project separates model-related files into three distinct areas:

1. **Model Weights** (`models/`):
   - Downloaded model weights and checkpoints
   - Model-specific cache files
   - Not tracked in git
   - Organized by model name

2. **Model Code** (`src/models/`):
   - Model implementations
   - Factory for model creation
   - Interface definitions
   - Common utilities

3. **Model Configuration** (`config/models/`):
   - Model parameters
   - Architecture settings
   - Training configurations
   - Inference settings

## Testing

The project uses pytest with comprehensive coverage:

1. Run all tests:
```bash
pytest tests/ -v
```

2. Run with coverage:
```bash
pytest tests/ -v --cov=src
```

3. Run specific test file:
```bash
pytest tests/test_config.py -v
```

Current test coverage:
- Configuration System: 97% coverage ✓
- Other components: In progress

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

3. **Documentation**:
   - Update ICD for interface changes
   - Document all public APIs
   - Include usage examples
   - Keep README current

4. **Git Workflow**:
   - Create feature branches
   - Write clear commit messages
   - Update tests with changes
   - Request reviews for PRs

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

## Dependency Injection ✓

The project follows strict dependency injection principles:

1. **Constructor Injection**:
   ```python
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

2. **Factory Pattern**:
   ```python
   class ServiceFactory:
       def create_service(self) -> BaseService:
           config = self.create_config()
           data_loader = self.create_data_loader(config)
           model = self.create_model(config)
           return Service(config, data_loader, model)
   ```

3. **Interface Dependencies**:
   ```python
   # Depend on interfaces, not implementations
   def process_data(data_loader: BaseDataLoader):
       data = data_loader.load_data()
       return process(data)
   ```

4. **Testing with Mocks**:
   ```python
   def test_service():
       mock_loader = Mock(spec=BaseDataLoader)
       mock_model = Mock(spec=BaseModel)
       service = Service(mock_loader, mock_model)
       assert service.process() == expected
   ```
