# Project To-Do: LMM Invoice Data Extraction Comparison

This to-do list is organized to prioritize local development work before moving to cloud-dependent tasks. Each task is designed to be a focused prompt for an LLM to implement.

## Phase 1: Project Setup and Foundation ✓

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

### 1.B: Data Management ✓
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

## Phase 2: Model Framework ✓

### 2.A: Base Framework ✓
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
- [x] 2.4 Implement error handling for model loading and inference
- [x] 2.5 Create model configuration validation utilities
      - Designed and implemented ValidationResult class for standardized results
      - Created ModelConfigValidator interface for consistent validation pattern
      - Implemented common validators (RequiredFieldValidator, TypeValidator)
      - Added CompositeValidator for combining validation rules
      - Integrated with BaseModelImpl for model-specific validation
      - Documented design decisions in ADR-006
      - Applied proper error handling with specific error types
      - Follows interface-based design principles
- [x] 2.6 Enhance dependency injection patterns for model components
      - [x] Review existing DI implementation from Phase 1
      - [x] Remove global state from configuration system
      - [x] Implement proper constructor-based DI
      - [x] Ensure type definitions are properly separated
      - [x] Create dependency graph documentation

## Phase 3: Prompt Management (Local Development)

### 3.A: Prompt Framework
- [x] 3.1 Implement BasePromptGenerator interface
- [x] 3.2 Create PromptFactory with proper test isolation and validation
- [ ] 3.3 Create PromptFormatter for model-specific prompt formatting
- [ ] 3.4 Implement remaining prompt strategies:
  - [ ] DetailedPromptGenerator
  - [ ] FewShotPromptGenerator
  - [ ] StepByStepPromptGenerator
  - [ ] LocationalPromptGenerator
  - [ ] TemplatePromptGenerator
- [ ] 3.5 Add comprehensive prompt validation:
  - [x] Work order format validation
  - [x] Cost format validation
  - [ ] Template validation
  - [ ] Example validation
- [ ] 3.6 Implement prompt caching system
- [ ] 3.7 Add performance benchmarks for prompt generation

### 3.B: Prompt Implementations
- [x] 3.6 Implement BasicPromptGenerator for direct extraction prompts
      - Created with interface-based design
      - Added comprehensive test suite (96% coverage)
      - Implemented template caching for performance
      - Added field-specific format instructions
      - Robust error handling with custom exceptions
      - Proper cleanup of resources
      - Follows dependency injection pattern
- [ ] 3.7 Implement DetailedPromptGenerator for detailed instruction prompts
- [ ] 3.8 Implement FewShotPromptGenerator for few-shot example prompts
- [ ] 3.9 Implement StepByStepPromptGenerator for guided extraction prompts
- [ ] 3.10 Implement LocationalPromptGenerator for spatial location prompts
- [ ] 3.11 Write prompt testing notebook to verify prompt framework works correctly

## Phase 4: Evaluation Framework (Local Development)

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

## Phase 5: Templates and Infrastructure (Local Development)

### 5.A: Experiment Template Framework
- [ ] 5.1 Create experiment_template.ipynb with standardized structure
- [ ] 5.2 Implement end-to-end workflow template
- [ ] 5.3 Add configuration options and parameter selection
- [ ] 5.4 Create basic result visualization in notebook

### 5.B: Analysis Infrastructure
- [ ] 5.5 Create results_analysis.ipynb structure for aggregating results
- [ ] 5.6 Implement result loading and merging functions
- [ ] 5.7 Create comparative visualization templates
- [ ] 5.8 Implement error analysis component templates

## Phase 6: Model Implementations (Cloud Development)

### 6.A: Model Implementation
- [ ] 6.1 Set up cloud development environment with GPU support
- [ ] 6.2 Implement PixtralModel class for Pixtral-12B model
- [ ] 6.3 Implement LlamaVisionModel class for Llama-3.2-11B-Vision model
- [ ] 6.4 Implement DoctrModel class for Doctr model
- [ ] 6.5 Create model-specific output parsing functions
- [ ] 6.6 Write model loading notebook to verify model framework works correctly

### 6.B: Initial Model Testing
- [ ] 6.7 Test experiment template with Pixtral-12B
- [ ] 6.8 Test experiment template with Llama-3.2-11B-Vision
- [ ] 6.9 Test experiment template with Doctr
- [ ] 6.10 Verify end-to-end workflow with small dataset

## Phase 7: MVP Evaluation (Cloud Development)

### 7.A: Initial Model Experiments
- [ ] 7.1 Run experiments with Pixtral-12B using different prompts
- [ ] 7.2 Run experiments with Llama-3.2-11B-Vision using different prompts
- [ ] 7.3 Run experiments with Doctr using different prompts
- [ ] 7.4 Run experiments on initial 20-image dataset
- [ ] 7.5 Collect and save results from all experiments

### 7.B: Initial Analysis and Refinement
- [ ] 7.6 Run analysis notebook on initial results
- [ ] 7.7 Identify and fix any issues with models or prompts
- [ ] 7.8 Refine evaluation metrics if needed
- [ ] 7.9 Document initial findings and observations
- [ ] 7.10 Prepare for expanded evaluation

## Phase 8: Expanded Evaluation (Cloud Development)

### 8.A: Full Dataset Experiments
- [ ] 8.1 Expand dataset to ~150 images
- [ ] 8.2 Update ground truth validation for expanded dataset
- [ ] 8.3 Run experiments with best-performing model/prompt combinations
- [ ] 8.4 Collect and analyze full results
- [ ] 8.5 Generate final comparison report

## Implementation Notes

1. **Local Development First**: Phases 3-5 can be completed entirely locally, maximizing development efficiency
2. **Infrastructure Before Implementation**: Build and test all frameworks before moving to model implementation
3. **Cloud Resource Optimization**: Cloud-dependent tasks are grouped to minimize resource usage
4. **Testing Strategy**: Each component can be tested independently with mock data
5. **Cost Efficiency**: Delays cloud resource usage until absolutely necessary

When implementing tasks:
1. Follow architectural principles from Phase 1
2. Maintain comprehensive test coverage
3. Document all major decisions
4. Use interface-based design consistently
5. Follow dependency injection patterns
