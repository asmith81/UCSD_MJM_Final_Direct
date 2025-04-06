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

### 4. Dependency Injection
- Dependencies should be passed explicitly to constructors
- Never use global state or singletons
- Make dependencies visible and traceable in code
- Use interface-based programming where appropriate
- Document dependencies clearly in class docstrings

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
- Validate all inputs at the boundaries
- Fail fast and explicitly
- Use appropriate exception types
- Provide clear error messages
- Clean up resources in case of errors

### Data Validation
- Validate field types during data loading
- Implement field-specific validation rules
- Log validation failures with detailed context
- Provide helpful error messages for data format issues
- Include original and attempted normalized values in errors
- Handle missing or malformed data gracefully
- Document expected data formats clearly

### Exception Guidelines
- Create custom exceptions for domain-specific errors
- Use built-in exceptions for standard errors
- Document exceptions in method docstrings
- Handle exceptions at appropriate levels

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

### Testing Approach
- Test critical components individually
- Verify end-to-end workflows with small test datasets
- Include challenging invoices in the test set
- Document testing approach
- Handle edge cases appropriately

### Data Validation Testing
- Test all supported data formats and variations
- Include edge cases for each field type:
  - Work Order Number: Leading zeros, special characters
  - Total Amount: Various currency formats, thousand separators
- Test data cleaning and normalization
- Verify error handling for invalid data
- Test caching behavior with large datasets
- Validate comparison strategies
- Document test data formats and variations