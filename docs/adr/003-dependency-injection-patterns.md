# 003. Dependency Injection Patterns

## Status

Accepted and Implemented

## Context

The system uses dependency injection (DI) extensively as a core architectural pattern, as outlined in the project rules under Core Architectural Principles. This ADR evaluates the current implementation of dependency injection, identifies strengths and areas for improvement, and provides recommendations for evolving the pattern as the system grows.

The existing implementation in Phase 1 components (ConfigLoader, DataLoader, GroundTruthManager, ImageProcessor) has established a foundation for DI, but we need to ensure consistency as we move to Phase 2 and 3 components.

## Evaluation of Current Implementation

### Strengths

1. **Constructor-Based Injection**: The codebase consistently uses constructor-based dependency injection, making component dependencies explicit and traceable.

2. **Interface-Based Dependencies**: Components depend on abstractions (interfaces/abstract classes) rather than concrete implementations, following the Dependency Inversion Principle.

3. **Factory Pattern Integration**: Factory classes (ConfigFactory, DataLoaderFactory, ImageProcessorFactory) create and configure concrete implementations, complementing the DI approach by centralizing object creation.

4. **High Testability**: The DI approach enables easy mocking and substitution of dependencies for testing, as demonstrated in the comprehensive test suite for Phase 1 components.

5. **Clear Separation of Concerns**: Components have well-defined boundaries and responsibilities, facilitated by the DI pattern, aligning with the project's architectural principles.

6. **No Global State**: Successfully eliminated all global state and singletons, particularly in the configuration system, ensuring proper dependency injection throughout.

### Implementation Examples

1. **Configuration System**:
   ```python
   # Interface-based design
   class BaseConfigManager(ABC):
       @abstractmethod
       def __init__(self, config_root: str, config_factory: ConfigFactory):
           pass
           
   # Constructor injection
   class ConfigManager(BaseConfigManager):
       def __init__(self, config_root: str, config_factory: ConfigFactory):
           if not config_root:
               raise ValueError("config_root must be provided")
           if not config_factory:
               raise ValueError("config_factory must be provided")
           self._config_root = config_root
           self._config_factory = config_factory
   ```

2. **Type System**:
   ```python
   # Separate type definitions
   class ConfigType(Enum):
       MODEL = auto()
       PROMPT = auto()
       EVALUATION = auto()
   ```

### Areas for Improvement

1. **Documentation**: The dependency relationships between components are not always well-documented in class docstrings, making it challenging to understand the full component graph.

2. **Component Granularity**: Some classes may have too many injected dependencies, suggesting they might have too many responsibilities.

## Decision

We will continue using constructor-based dependency injection as our primary DI pattern but will make the following improvements:

1. Establish clearer guidelines for dependency management in upcoming components
2. Consider introducing a lightweight DI container for managing the larger component graphs in Phases 2-4
3. Document component relationships more explicitly in class docstrings
4. Review components with many dependencies for potential refactoring to maintain the maximum 5 arguments per function constraint

## Guidelines for Implementation

1. **All Dependencies Should Be Explicit**:
   - Always inject dependencies through constructors
   - Document each dependency's purpose in constructor docstrings
   - Avoid service locator patterns or global state

2. **Interface-Based Design**:
   - Dependencies should be on interfaces/abstract classes, not concrete implementations
   - Each major component should have a corresponding interface
   - Interfaces should be in dedicated files (e.g., `base_*.py`)

3. **Factory Pattern Usage**:
   - Use factory classes to create complex objects
   - Factories should handle dependency creation and wiring
   - Register implementations with factories rather than hardcoding them

4. **Type System Organization**:
   - Keep type definitions in separate modules
   - Avoid circular dependencies through proper module organization
   - Use enums for type definitions where appropriate

5. **Testing Considerations**:
   - Design components to be testable in isolation
   - Provide mock implementations for testing complex dependencies
   - Use constructor injection to enable easy dependency mocking

## Consequences

### Positive

- Increased modularity and component independence
- Better testability and easier mocking
- Clearer component boundaries and responsibilities
- More flexible system evolution through loose coupling
- Elimination of global state and singletons
- Proper separation of type definitions

### Negative

- Slightly increased boilerplate code
- Need for more documentation to understand component relationships

### Neutral

- Need to train new team members on the DI patterns
- Regular architecture reviews to ensure adherence to patterns

## Next Steps

1. Document the current component dependency graph for Phase 1 components
2. Apply these guidelines strictly to upcoming Phase 2 and 3 components:
   - ModelFactory and Model implementations
   - PromptFactory and Prompt strategy implementations
   - OutputParser and EvaluationService
3. Evaluate lightweight DI containers for potential adoption in Phase 4
4. Update project_rules.md with expanded dependency injection guidelines
5. Establish code review criteria specific to dependency management 