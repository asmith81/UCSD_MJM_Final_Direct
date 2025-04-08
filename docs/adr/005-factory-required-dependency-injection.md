# ADR 005: Required Dependency Injection for Factory Classes

## Status
Accepted

## Context
Our codebase included factory classes (ModelFactory, OutputParserFactory, PromptFactory) that relied on global configuration systems. 
These factories had constructors that allowed optional configuration manager parameters with fallbacks to global state:

```python
def __init__(self, config_manager=None):
    self._config_manager = config_manager or get_config_manager()
```

This pattern created several issues:
1. Testing was difficult without patching the global configuration system
2. Dependencies were implicit rather than explicit
3. The code violated our architectural principle that "dependencies should be passed explicitly to constructors"
4. Global state created tight coupling between components

During testing, we discovered these issues when attempts to unit test factories required complex setup or patching of global state.

## Decision
We decided to implement required dependency injection for all factory classes by:

1. Modifying factory constructors to require a configuration manager:
```python
def __init__(self, config_manager):
    if config_manager is None:
        raise ValueError("config_manager is required")
    self._config_manager = config_manager
```

2. Updating all code that instantiates factory classes to explicitly provide a configuration manager
3. Updating tests to properly inject mock configuration managers
4. Creating clear documentation of the pattern for developers

This approach was applied to:
- ModelFactory
- OutputParserFactory 
- PromptFactory
- EvaluationService

## Consequences

### Positive
1. **Improved Testability**: Dependencies can be easily mocked in tests without patching
2. **Explicit Dependencies**: All dependencies are now visible in the code
3. **Architectural Alignment**: Code follows our core principle of explicit dependency injection
4. **Decoupling**: Components are no longer tightly coupled to global state
5. **Better Error Messages**: Failures happen at construction time with clear error messages

### Negative
1. **Migration Effort**: All code that creates factory instances needed updating
2. **Slightly More Verbose**: Code that uses factories now needs to obtain and pass a config manager
3. **Breaking Change**: Existing code that used the default parameter needs modification

### Neutral
1. **Consistency**: All factory classes now follow the same pattern
2. **Documentation**: Created additional documentation to explain the pattern

## Alternatives Considered

### Option 1: Keep the Optional Parameter but Lazy-Load
We could have maintained the optional parameter but only attempted to get the global instance when needed:
```python
def create_model(self, model_name, config=None):
    if config is None:
        if self._config_manager is None:
            self._config_manager = get_config_manager()
        # Use self._config_manager
```

This would maintain backward compatibility but still rely on global state and wouldn't fully address the architectural issues.

### Option 2: Use the injector Package
The project includes the `injector` package in requirements.txt. We could have implemented a more sophisticated dependency injection system using this package. While this might provide additional features, it would be a more complex change and might require significant refactoring.

### Option 3: Create Factory Providers
We could have implemented a provider pattern to abstract the creation of factories, but this would add another layer of indirection without fully addressing the root issue.

## Implementation Notes
The implementation required changes to:
1. Factory class constructors
2. Tests that create factory instances
3. Any application code that instantiates factories

Documentation was created in `dependency_injection_guide.md` to explain the pattern and help developers update their code.

## References
- [Core Architectural Principles](../rules/core-architectural-principals.mdc)
- [ADR 003: Dependency Injection Patterns](./003-dependency-injection-patterns.md) 