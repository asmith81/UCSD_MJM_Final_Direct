# Dependency Injection Improvement Tasks

## Background
Our codebase effectively uses dependency injection as a core architectural pattern, as outlined in the project rules and implemented in Phase 1 components. As we move into Phase 2 and 3, we need to strengthen and standardize our approach to ensure maintainability and scalability.

## Current Implementation Status
- Phase 1 components (ConfigLoader, DataLoader, GroundTruthManager, ImageProcessor) have established a good foundation for DI
- Factory patterns have been implemented consistently
- Interface-based design is being followed
- Tests demonstrate the benefits of DI for mocking and isolation
- BaseModel abstract class implemented with proper DI patterns and comprehensive testing
- [x] Basic dependency injection patterns established in core components
- [x] Factory classes implemented with error handling and recovery mechanisms
- [x] Model initialization with configuration-based dependency injection
- [x] Configuration system refactored to eliminate global state
- [x] Type system properly separated to avoid circular dependencies
- [ ] Comprehensive dependency graph documentation

## Improvement Tasks

### 1. Dependency Graph Documentation
- [x] Create a visual diagram of current component dependencies for Phase 1
- [x] Document the planned dependency graph for Phase 2 components
- [x] Identify potential circular dependencies or complex dependency chains
- [x] Add the dependency graph to the architecture documentation

### 2. Standardize Factory Classes for Phase 2-3
- [x] Ensure BaseModel follows established interface and DI patterns
- [x] Complete ModelFactory implementation following existing factory patterns
- [x] Implement OutputParserFactory with proper registration and DI patterns
- [x] Implement ConfigFactory with proper type handling and validation
- [ ] Implement PromptFactory with consistent registration mechanisms
- [x] Add detailed documentation to factory classes about their role in DI
- [x] Update factory class tests to verify proper dependency handling

### 3. Dependency Container Evaluation
- [ ] Research lightweight DI containers compatible with our architecture
- [ ] Create a small proof of concept using the most promising option
- [ ] Test with Phase 1 components before introducing to Phase 2
- [ ] Document findings and make recommendations in an updated ADR

### 4. Component Granularity Review
- [x] Identify any components with > 4 dependencies
- [x] Review against the 5-argument constraint in project rules
- [ ] Propose refactoring strategies for complex components
- [ ] Update class structure to maintain clear separation of concerns

### 5. Enhance Constructor Documentation
- [x] Add detailed docstrings for all constructor parameters
- [x] Document the purpose and expected behavior of each dependency
- [x] Highlight optional vs. required dependencies
- [x] Expand existing test fixtures to validate dependency behavior

### High Priority

#### [x] Create an interface-based configuration system
Create abstract base classes and protocols for configuration components to allow for different implementations. This should include separate interfaces for model configuration, prompt configuration, and evaluation configuration.

#### [x] Implement a factory for configuration objects
Create a factory class that can instantiate the appropriate configuration object based on runtime parameters, allowing for flexibility in configuration selection.

#### [x] Set up dependency injection for the main components
Implement proper constructor-based DI for major components like model handlers, data loaders, and configuration services.

#### [x] Create a modular data loading system with DI
Refactor the data loading system to use interfaces and DI, allowing for different data sources to be used interchangeably through the same interface.

#### [x] Implement model configuration validation utilities
Create a validation system that can verify model configurations against API requirements and resource constraints before runtime execution. This should include validation result classes, validator interfaces, and basic validator implementations.

#### [x] Replace direct imports with proper DI
- [x] Remove global state and singletons
- [x] Implement proper constructor-based DI
- [x] Ensure type definitions are properly separated

#### [x] Standardize factory classes across the codebase
  - Completed: ModelFactory and ConfigFactory implementations serve as templates with robust error handling

#### [ ] Create and maintain dependency graph documentation

### Medium Priority

## Completion Criteria
- [x] All Phase 1 components follow consistent DI patterns
- [x] Factory classes handle dependency creation uniformly
- [x] Component dependencies are clearly documented in code
- [ ] High-dependency components are refactored into more focused units
- [ ] A decision is made regarding potential DI container adoption

## Implementation Notes
- Configuration system refactored to use proper DI:
  - BaseConfigManager interface with clear methods and dependencies
  - ConfigManager with constructor-based DI
  - ConfigFactory with type-safe configuration creation
  - ConfigType enum properly separated to avoid circular dependencies
  - High test coverage (95-100%) with test fixtures demonstrating DI benefits

- OutputParser system implemented with proper DI patterns:
  - BaseOutputParser interface with clear methods and dependencies
  - OutputParserFactory with registration mechanism and proper error handling
  - ExtractedFieldsOutputParser with injectable validator dependencies
  - High test coverage (85-100%) with test fixtures demonstrating DI benefits

- Model Configuration Validation Utilities implemented with proper DI patterns:
  - ValidationResult class for standardized validation results
  - ModelConfigValidator interface for consistent validator behavior
  - Injectable validators through constructor dependency injection
  - CompositeValidator demonstrating composition of validators
  - Integration with BaseModelImpl through template method pattern
  - Follows interface-based design principles outlined in ADR-006

## References
- [ADR-003: Dependency Injection Patterns](../docs/adr/003-dependency-injection-patterns.md)
- [ADR-006: Model Configuration Validation Utilities](../docs/adr/006-model-configuration-validation.md)
- [Project Rules: Dependency Injection Section](project-rules.md)
- [Architecture Diagram](architecture-diagram.md) 