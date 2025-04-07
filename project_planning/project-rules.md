Here's the Project Rules artifact:

# Project Rules: LMM Invoice Data Extraction Comparison

## IMPORTANT: Pre-Development Requirements
- Review the Project Overview & Plan document completely before writing any code
- Study the System Architecture document to understand component relationships
- Consult the Project Directory Structure document to maintain proper organization
- Refer to this rules document when making any implementation decisions

## Core Architectural Principles

### 1. Simplicity and Clarity
- Keep all implementations as simple and direct as possible
- Favor explicit over implicit code
- Prioritize readability over cleverness
- Maintain a clean, consistent style throughout the codebase
- Document all design decisions and non-obvious implementations

### 2. Code Constraints
- Maximum 550 lines per file - NO EXCEPTIONS
- Maximum 100 characters per line
- Maximum 25 lines per function/method
- Maximum 5 arguments per function
- Maximum 3 levels of nesting in any function

### 3. Separation of Concerns
- Each class must have a single, well-defined responsibility
- Each module must have a clear purpose
- Avoid mixing concerns (e.g., data loading and model inference)
- Create boundaries between system components
- Components should be able to evolve independently
- Interfaces and implementations must be separate

### 4. Project Structure and Organization
- Follow this standard directory structure for components:
  ```
  src/
    component_name/
      base_component.py          # Interface definition
      component_factory.py       # Factory implementation
      implementations/           # Concrete implementations
        implementation1.py
        implementation2.py
      tests/
        test_component.py        # Interface tests
        test_component_factory.py # Factory tests
  ```
- Use relative imports for module references:
  ```python
  # In component_factory.py
  from .base_component import BaseComponent  # Same directory
  from .implementations.impl1 import Impl1   # Child directory
  
  # In implementations/impl1.py
  from ..base_component import BaseComponent  # Parent directory
  ```
- Avoid absolute imports that break modularity
- Do not import concrete implementations in factory files

### 5. Interface-Based Design
- Define clear interfaces (abstract base classes or protocols) for all major components
- Depend on abstractions, not concrete implementations
- Use registration pattern for factory implementations
- Document interfaces thoroughly with expected behavior
- Follow this pattern for factory implementation:
  ```python
  # Interface (base_component.py)
  from abc import ABC, abstractmethod
  
  class BaseComponent(ABC):
      @abstractmethod
      def process(self, input: Any) -> Any:
          """Process input data."""
          pass
  
  # Factory (component_factory.py)
  class ComponentFactory:
      # Empty registry - no concrete implementations
      REGISTRY: Dict[str, Type[BaseComponent]] = {}
      
      @classmethod
      def register(cls, name: str, implementation: Type[BaseComponent]):
          """Register an implementation."""
          cls.REGISTRY[name] = implementation
      
      def create(self, name: str, config: Config) -> BaseComponent:
          """Create component by name."""
          if name not in self.REGISTRY:
              raise ValueError(f"Unknown component: {name}")
          return self.REGISTRY[name]()
  ```

### 6. State Management
- Avoid global state entirely
- If state must be shared, use explicit state containers
- Prefer immutable state when possible
- Make all state changes trackable and visible
- Reinitialize all global state when needed (such as in tests)
- Example of proper state management:
  ```python
  # BAD - Global state
  CACHE = {}
  
  def process(key):
      if key in CACHE:
          return CACHE[key]
      result = compute(key)
      CACHE[key] = result
      return result
  
  # GOOD - Injectable state
  class Processor:
      def __init__(self, cache=None):
          self._cache = cache or {}
          
      def process(self, key):
          if key in self._cache:
              return self._cache[key]
          result = self._compute(key)
          self._cache[key] = result
          return result
  ```

### 7. Dependency Injection
- Dependencies should be passed explicitly to constructors
- Never use global state or singletons
- Make dependencies visible and traceable in code
- Use interface-based programming where appropriate
- Document dependencies clearly in class docstrings
- Avoid module-level imports of concrete implementations
- Prefer dependency injection techniques:
  ```python
  # BAD
  from .database import Database
  
  class Service:
      def __init__(self):
          self.db = Database()  # Hardcoded dependency
  
  # GOOD
  from .base_database import BaseDatabase
  
  class Service:
      def __init__(self, database: BaseDatabase):
          self.db = database  # Injected dependency
  ```

## Naming Conventions

### Class Names
- CamelCase for all class names
- Descriptive, purpose-indicating names
- Model classes: `[ModelName]Model` (e.g., `LlavaModel`)
- Configuration classes: `[Component]Config` (e.g., `PromptConfig`)
- Service classes: `[Purpose]Service` (e.g., `EvaluationService`)
- Factory classes: `[Product]Factory` (e.g., `ModelFactory`)

### Method Names
- snake_case for all method names
- Verb phrases describing actions
- Initialization methods: `initialize_[resource]` (e.g., `initialize_model`)
- Processing methods: `process_[data]` (e.g., `process_image`)
- Evaluation methods: `evaluate_[metric]` (e.g., `evaluate_accuracy`)
- Getter methods: `get_[attribute]` (e.g., `get_config`)

### Variable and Parameter Names
- snake_case for all variable and parameter names
- Descriptive names indicating purpose and type
- Configuration objects: `[component]_config` (e.g., `model_config`)
- Service objects: `[service]_service` (e.g., `evaluation_service`)
- Manager objects: `[resource]_manager` (e.g., `data_manager`)
- Factory objects: `[product]_factory` (e.g., `model_factory`)

### File Names
- snake_case for all file names
- Descriptive, purpose-indicating names
- One class per file (with rare exceptions for small, related classes)
- File name should match primary class name (converting CamelCase to snake_case)
- Test files: `test_[module_name].py`

## Documentation Requirements

### Class Documentation
- Every class must have a docstring explaining:
  - Purpose of the class
  - Responsibilities
  - Dependencies
  - Example usage (if not trivial)

### Method Documentation
- Every public method must have a docstring explaining:
  - Purpose of the method
  - Parameters (with types and descriptions)
  - Return value (with type and description)
  - Exceptions raised (if any)
  - Example usage (for complex methods)

### Module Documentation
- Every module must have a docstring explaining:
  - Purpose of the module
  - Classes/functions contained
  - Usage examples (if appropriate)

## Error Handling

### Error Principles
- Validate all inputs at system boundaries
- Fail fast and explicitly with detailed error messages
- Use domain-specific exception types
- Provide clear, actionable error messages
- Clean up resources in case of errors
- Never swallow exceptions without logging

### Exception Hierarchy
- Define a clear exception hierarchy for each domain:
  ```python
  # Base domain exception
  class DomainError(Exception):
      """Base exception for domain-specific errors."""
      pass
      
  # Component-specific exceptions
  class ModelError(DomainError):
      """Base exception for model-related errors."""
      pass
      
  # Specific error conditions
  class ModelInitializationError(ModelError):
      """Raised when model initialization fails."""
      pass
      
  class ModelProcessingError(ModelError):
      """Raised when model processing fails."""
      pass
  ```

### Input Validation
- Validate all inputs as early as possible:
  ```python
  def process_image(image_path):
      # Validate input
      if not isinstance(image_path, Path):
          raise TypeError("Image path must be a Path object")
          
      if not image_path.exists():
          raise FileNotFoundError(f"Image not found: {image_path}")
          
      if not image_path.suffix.lower() in {'.jpg', '.png', '.jpeg'}:
          raise ValueError(f"Unsupported image format: {image_path.suffix}")
          
      # Process after validation
      return _process_image_impl(image_path)
  ```

### Exception Handling Patterns
- Convert low-level exceptions to domain-specific ones:
  ```python
  try:
      result = external_library.process(data)
  except ExternalLibraryError as e:
      # Convert to domain-specific exception
      raise DomainError(f"Processing failed: {e}") from e
  ```
- Use context managers for resource cleanup:
  ```python
  def process_file(file_path):
      try:
          with open(file_path, 'r') as f:
              data = f.read()
          return process_data(data)
      except IOError as e:
          raise FileProcessingError(f"Failed to read {file_path}: {e}") from e
  ```

### Error Reporting
- Include relevant context in error messages:
  ```python
  # BAD - Generic message
  raise ValueError("Invalid value")
  
  # GOOD - Specific message with context
  raise ValueError(f"Invalid value for field '{field_name}': expected {expected}, got {actual}")
  ```
- Log errors at appropriate levels:
  ```python
  try:
      process_data(data)
  except ValidationError as e:
      # Client error - not severe
      logger.warning(f"Validation failed: {e}")
      raise
  except SystemError as e:
      # Server error - severe
      logger.error(f"System error: {e}", exc_info=True)
      raise
  ```

## Component-Specific Rules

### Data Management
- Field types must be explicitly defined and documented
- Data cleaning and normalization must occur during loading
- Implement field-specific validation rules:
  - Work Order Number: Preserve leading zeros and format
  - Total Amount: Clean currency symbols and normalize decimals
- Provide clear error messages for validation failures
- Document data type transformations in docstrings
- Implement robust comparison strategies for each field type
- Cache normalized data when appropriate
- Log all data cleaning and transformation operations

### Configuration Management
- All configuration should be in YAML files
- No hardcoded configuration values in code
- Validate configuration on loading
- Provide sensible defaults where appropriate
- Document all configuration options

### Model Management
- Use factory pattern for model creation
- Ensure consistent interface across all models
- Handle resources appropriately (load/unload)
- Document model capabilities and limitations
- Clear separation between model and inference logic

### Prompt Management
- Use template pattern for prompt generation
- Document prompt strategies clearly
- Ensure prompts are configurable via YAML
- Keep prompt logic separate from model logic
- Version prompt templates explicitly

### Evaluation Framework
- Clearly define all metrics
- Consistent evaluation across all models/prompts
- Document evaluation methodology
- Store results in standardized format
- Provide clear visualizations of results

## Notebook Rules

### Structure
- Each notebook must be self-contained
- Clear separation between configuration and execution
- Standard sections: imports, configuration, execution, results
- No business logic in notebooks
- Results should be saved to disk in standardized format

### Style
- Use markdown cells for section headers
- Keep code cells short and focused
- Include comments explaining complex operations
- Use standard variable names across notebooks
- Clean up resources explicitly when done

## Quality Assurance

### Code Quality
- Maintain consistent style throughout
- Follow all naming conventions
- Document all public classes and methods
- Keep functions small and focused
- Avoid code duplication

### Testing Architecture
- Every component must have a comprehensive test suite:
  ```
  tests/
    test_component.py         # Interface tests
    test_component_factory.py # Factory tests
    test_implementations/     # Implementation tests
  ```
- Tests must be independent and isolable:
  - Each test must run correctly on its own
  - Order of test execution should not matter
  - No shared state between tests without explicit fixtures
  - Global state must be restored after each test

### Test Fixtures and Dependencies
- Properly manage test dependencies:
  ```python
  # Global state reset fixture
  @pytest.fixture(autouse=True)
  def reset_global_state():
      """Reset global state before and after each test."""
      Registry.clear()  # Before test
      yield
      Registry.clear()  # After test
  
  # Mock dependency fixture
  @pytest.fixture
  def mock_dependency():
      """Create isolated mock dependency."""
      with patch("module.Dependency") as mock:
          mock.return_value.method.return_value = "test"
          yield mock
  
  # Component under test fixture
  @pytest.fixture
  def component(mock_dependency):
      """Create isolated component instance for testing."""
      return Component(dependency=mock_dependency)
  ```

### Testing Approach
- Test critical components individually
- Verify end-to-end workflows with small test datasets
- Include challenging edge cases in test data
- Document testing approach in test module docstrings
- Handle edge cases appropriately
- Explicitly verify error conditions and exceptions:
  ```python
  def test_error_handling(component):
      """Test that errors are properly handled."""
      with pytest.raises(ExpectedException, match="Expected message"):
          component.method_with_error()
  ```

### Mock Management
- Use proper mocking techniques:
  ```python
  # Incorrect - Mock too general
  @patch("module.Class")
  def test_bad(mock_class):
      instance = module.Class()
  
  # Correct - Mock specific to test
  @patch("module.Class.method")
  def test_good(mock_method):
      mock_method.return_value = "test"
      instance = module.Class()
      result = instance.method()
  ```
- Avoid over-mocking:
  - Only mock external dependencies
  - Use real implementations for unit-internal code
  - Document mock behavior in fixture docstrings

### Test Coverage
- Maintain minimum 80% code coverage
- All public methods must be tested
- All error conditions must be verified
- All configuration options must be tested
- Check coverage regularly with:
  ```bash
  python -m pytest --cov=src tests/
  ```

### Data Validation Testing
- Test all supported data formats and variations
- Include edge cases for each field type
- Test data cleaning and normalization
- Verify error handling for invalid data
- Test caching behavior with large datasets
- Validate comparison strategies
- Document test data formats and variations