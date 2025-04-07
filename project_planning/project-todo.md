# Project To-Do: LMM Invoice Data Extraction Comparison

This to-do list is organized in sequential implementation order by phases and sub-phases. Each task is designed to be a focused prompt for an LLM to implement. Complete each phase before moving to the next.

## Phase 1: Project Setup and Foundation

### 1.A: Project Structure and Configuration ✓
- [x] 1.1 Initialize project repository with directory structure
- [x] 1.2 Create README.md with project overview and setup instructions
- [x] 1.3 Create requirements.txt with initial dependencies
- [x] 1.4 Implement ConfigLoader class to load YAML configurations
      - Implemented with dependency injection
      - Added comprehensive test suite (97% coverage)
      - Created ConfigParser protocol and YAMLConfigParser
- [x] 1.5 Define base configuration structures
      - BaseConfig interface
      - ModelConfig implementation
      - PromptConfig implementation
      - EvaluationConfig implementation
- [x] 1.6 Create sample configuration YAML files for models and prompts
      - Model configuration templates
      - Prompt configuration templates
      - Evaluation configuration templates

Section completed with all requirements satisfied and following architectural principles:
- Interface-based design
- Dependency injection
- Comprehensive testing
- Clear separation of concerns

### 1.B: Data Management
- [x] 1.7 Implement DataLoader class to load images and ground truth CSV
      - Implemented with interface-based design (BaseDataLoader)
      - Added comprehensive test suite (94% coverage)
      - Includes caching mechanism and error handling
      - Custom exceptions for data validation and loading errors
- [x] 1.8 Implement GroundTruthManager to parse and validate ground truth data
      - Implemented with proper dependency injection
      - Added comprehensive test suite (96% coverage)
      - Field-specific data type handling:
        - Total Amount: Float with 2 decimal places, cleaned during load
        - Work Order Number: Format-preserving string
      - Includes caching mechanism and validation
      - Custom exceptions and error handling
      - Documented in ADR-001 for data type decisions
- [x] 1.9 Implement ImageProcessor for basic image preprocessing
      - Created ImageProcessor interface and implementation
      - Added configuration system with validation
      - Implemented factory pattern
      - Added comprehensive test suite
      - Created usage examples

- [x] 1.10 Create utility functions for data validation and visualization
      - Implemented ValidationUtils for validating data files and directories
      - Created FieldValidators for type-specific validation and normalization
      - Developed DataVisualizer for exploratory data visualization 
      - Built validators using dependency injection pattern
      - Added comprehensive test suite for validators (92-98% coverage)
      - Documented validation strategies and visualization approaches
      - Applied interface-based design with BaseValidator abstract class
      - Fixed test configuration issues to ensure test suite passes
      
- [x] 1.11 Write data loading notebook to verify data pipeline works correctly
      - Implemented data_loading_verification.ipynb with proper project setup
      - Verified DataLoader factory instantiation
      - Successfully loaded and validated ground truth data with 29 rows
      - Confirmed image loading functionality works correctly
      - Demonstrated data format integrity and pipeline operations
      - Generated summary statistics for dataset exploration

Section completed with all requirements satisfied and following architectural principles:
- Interface-based design
- Dependency injection
- Comprehensive testing
- Clear separation of concerns
- Proper data validation and integrity checks

## Phase 2: Model Integration

### 2.A: Model Framework
- [x] 2.1 Define BaseModel abstract class with standard interface
      - Implemented with proper interface-based design
      - Added comprehensive test suite (83% coverage)
      - Created custom exceptions for error handling
      - Follows dependency injection pattern
      - Includes proper documentation and type hints
- [x] 2.2 Implement ModelFactory for creating model instances
      - Created with registration pattern to avoid hard dependencies
      - Added comprehensive test suite (95% coverage)
      - Implemented proper dependency injection
      - Created robust error handling and validation
      - Documented with ADR-004 for factory registration pattern
      - Enhanced project rules with specific factory implementation guidance
      - Used interface-based design with no concrete implementation dependencies
- [x] 2.3 Create OutputParser for extracting structured data from model outputs
      - Implemented with interface-based design (BaseOutputParser)
      - Added registration-based OutputParserFactory
      - Created ExtractedFieldsOutputParser as primary implementation
      - Comprehensive test suite with 85-90% coverage
      - Supports multiple output formats (JSON, key-value pairs, plain text)
      - Field name normalization for variant handling
      - Integrated with field validators for type-specific normalization
      - Robust error handling with custom exceptions
      - Follows dependency injection pattern
- [ ] 2.4 Implement error handling for model loading and inference
- [ ] 2.5 Create model configuration validation utilities
- [ ] 2.6 Enhance dependency injection patterns for model components
      - Review existing DI implementation from Phase 1
      - Apply consistent DI patterns to model components
      - Document component relationships and dependencies
      - Create comprehensive test suite using DI for mocking
      - See di-improvement-tasks.md for detailed sub-tasks

### 2.B: Model Implementations
- [ ] 2.7 Implement PixtralModel class for Pixtral-12B model
- [ ] 2.8 Implement LlamaVisionModel class for Llama-3.2-11B-Vision model
- [ ] 2.9 Implement DoctrModel class for Doctr model
- [ ] 2.10 Create model-specific output parsing functions
- [ ] 2.11 Write model loading notebook to verify model framework works correctly

## Phase 3: Prompt Management

### 3.A: Prompt Framework
- [ ] 3.1 Define BasePromptGenerator abstract class with standard interface
- [ ] 3.2 Implement PromptFactory for creating prompt generators
- [ ] 3.3 Create PromptFormatter for model-specific prompt formatting
- [ ] 3.4 Implement prompt template loading and validation
- [ ] 3.5 Create utility functions for prompt visualization

### 3.B: Prompt Implementations
- [ ] 3.6 Implement BasicPromptGenerator for direct extraction prompts
- [ ] 3.7 Implement DetailedPromptGenerator for detailed instruction prompts
- [ ] 3.8 Implement FewShotPromptGenerator for few-shot example prompts
- [ ] 3.9 Implement StepByStepPromptGenerator for guided extraction prompts
- [ ] 3.10 Implement LocationalPromptGenerator for spatial location prompts
- [ ] 3.11 Write prompt testing notebook to verify prompt framework works correctly

## Phase 4: Evaluation Framework

### 4.A: Evaluation Components
- [ ] 4.1 Implement MetricsCalculator for accuracy and CER metrics
- [ ] 4.2 Implement EvaluationService to orchestrate evaluation
- [ ] 4.3 Create ResultsManager for saving and loading results
- [ ] 4.4 Implement result validation and normalization utilities
- [ ] 4.5 Create standard result format definitions

### 4.B: Visualization and Analysis
- [ ] 4.6 Implement VisualizationService for creating visualizations
- [ ] 4.7 Create ComparisonPlotter for model/prompt comparisons
- [ ] 4.8 Implement ResultsTable for tabular result display
- [ ] 4.9 Create utility functions for error analysis
- [ ] 4.10 Write evaluation testing notebook to verify metrics calculation

## Phase 5: Integration and Initial Testing

### 5.A: Experiment Notebook Template
- [ ] 5.1 Create experiment_template.ipynb with standardized structure
- [ ] 5.2 Implement end-to-end workflow in template
- [ ] 5.3 Add configuration options and parameter selection
- [ ] 5.4 Create basic result visualization in notebook
- [ ] 5.5 Test template with a single model/prompt combination

### 5.B: Analysis Notebook
- [ ] 5.6 Create results_analysis.ipynb for aggregating results
- [ ] 5.7 Implement result loading and merging functions
- [ ] 5.8 Create comparative visualizations across models and prompts
- [ ] 5.9 Implement error analysis components
- [ ] 5.10 Test analysis notebook with sample results

## Phase 6: MVP Evaluation

### 6.A: Initial Model Experiments
- [ ] 6.1 Create experiment notebooks for Pixtral-12B with different prompts
- [ ] 6.2 Create experiment notebooks for Llama-3.2-11B-Vision with different prompts
- [ ] 6.3 Create experiment notebooks for Doctr with different prompts
- [ ] 6.4 Run experiments on initial 20-image dataset
- [ ] 6.5 Collect and save results from all experiments

### 6.B: Initial Analysis and Refinement
- [ ] 6.6 Run analysis notebook on initial results
- [ ] 6.7 Identify and fix any issues with models or prompts
- [ ] 6.8 Refine evaluation metrics if needed
- [ ] 6.9 Document initial findings and observations
- [ ] 6.10 Prepare for expanded evaluation

## Phase 7: Expanded Evaluation

### 7.A: Full Dataset Experiments
- [ ] 7.1 Expand dataset to ~150 images
- [ ] 7.2 Update ground truth validation for expanded dataset
- [ ] 7.3 Run experiments with best-performing model/prompt combinations
- [ ] 7.4 Collect and save results from expanded experiments
- [ ] 7.5 Verify result consistency across dataset sizes

### 7.B: Final Analysis and Documentation
- [ ] 7.6 Run analysis notebook on full results
- [ ] 7.7 Create comprehensive performance comparisons
- [ ] 7.8 Identify best-performing model/prompt combination
- [ ] 7.9 Document findings and recommendations
- [ ] 7.10 Prepare final presentation materials

## Implementation Priorities

1. **Core Framework First**: Build the foundational components before specific implementations
2. **One Working Example**: Get a single model/prompt combination working end-to-end before adding more
3. **Incremental Testing**: Test each component individually before integration
4. **Documentation As You Go**: Document each component as it's implemented
5. **Small, Focused Tasks**: Keep implementation tasks small and focused for easier LLM prompting

## Implementation Notes for LLM Prompting

When prompting an LLM to implement a task:

1. Provide the exact class name and file location
2. Reference relevant project rules (naming conventions, etc.)
3. Specify required methods and interfaces
4. Include example usage if helpful
5. Mention dependencies and relationships with other components
6. Request proper documentation and error handling

Example prompt format:
```
Implement the ConfigLoader class in src/config/config_loader.py according to the project rules.
This class should load and validate YAML configuration files.

Required methods:
- __init__(self, config_path)
- load(self) -> Config
- validate(self, config) -> bool

Dependencies:
- Uses PyYAML for loading YAML files
- Returns appropriate Config objects (ModelConfig, PromptConfig, etc.)

Include proper error handling and documentation.
```
