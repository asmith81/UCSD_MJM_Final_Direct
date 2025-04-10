# ADR-007: Prompt Generation System Design

## Status
Accepted

## Context
The system needs a flexible way to generate prompts for different models and field types, with support for multiple prompt strategies and proper validation.

## Decision

### Core Components
1. Base interface (`BasePromptGenerator`)
2. Factory pattern (`PromptFactory`)
3. Configuration system (`PromptConfig`)
4. Template management
5. Multiple prompt strategies

### Test Requirements
1. Test Isolation
   - All tests must properly isolate class-level state
   - Registry must be cleared between tests
   - Active generators must be cleaned up
   - Default registration must be controlled in tests

2. Validation Requirements
   - Field-specific validation (work order, cost, etc.)
   - Format validation using field validators
   - Example validation in templates
   - Proper error propagation

### Implementation Details
1. Factory Pattern
   - Class-level registry for generators
   - Dynamic registration system
   - Proper cleanup of resources
   - Clear validation rules

2. Configuration
   - YAML-based configuration
   - Field-specific requirements
   - Format instructions
   - Example validation

3. Error Handling
   - Domain-specific exceptions
   - Detailed error messages
   - Proper cleanup on errors
   - Validation at boundaries

### Testing Strategy
1. Test Categories
   - Source code tests (implementation correctness)
   - Test function tests (test methodology)
   - Integration tests (component interaction)

2. Test Fixtures
   - Registry management
   - Configuration setup
   - Mock generators
   - Resource cleanup

3. Validation Testing
   - Field format validation
   - Example validation
   - Error conditions
   - Edge cases

## Consequences

### Positive
1. Clear separation of concerns
2. Flexible prompt generation
3. Strong validation
4. Proper test isolation
5. Resource management

### Negative
1. Additional complexity in test setup
2. Need for careful state management
3. More boilerplate code

### Mitigations
1. Automated test fixtures
2. Clear documentation
3. Strong typing
4. Comprehensive test coverage

## Implementation Notes

### Factory Implementation
```python
class PromptFactory:
    REGISTRY: Dict[str, Type[BasePromptGenerator]] = {}
    VALID_CATEGORIES = {'basic', 'detailed', 'positioned', 'few_shot', 'step_by_step', 'template'}
    
    @classmethod
    def register_generator(cls, category: str, generator_class: Type[BasePromptGenerator]) -> None:
        if category not in cls.VALID_CATEGORIES:
            raise ValueError(f"Invalid category: {category}")
        if registry_key in cls.REGISTRY:
            raise ValueError(f"Category already registered: {category}")
        cls.REGISTRY[category] = generator_class
```

### Test Implementation
```python
@pytest.fixture(autouse=True)
def clear_registry():
    """Clear the PromptFactory registry before each test."""
    PromptFactory.REGISTRY.clear()
    PromptFactory._active_generators.clear()
    original_register = PromptFactory._register_default_generators
    PromptFactory._register_default_generators = lambda self: None
    yield
    PromptFactory._register_default_generators = original_register
    PromptFactory.REGISTRY.clear()
    PromptFactory._active_generators.clear()
```

### Validation Implementation
```python
def _validate_config(self, config: BaseConfig, category: str, field_type: str) -> bool:
    try:
        if not isinstance(config, PromptConfig):
            raise PromptConfigError("Configuration must be a PromptConfig instance")
            
        # Field-specific validation
        if field_type == 'work_order':
            is_valid, error_msg, _ = validate_work_order(output)
            if not is_valid:
                raise PromptConfigError(f"Invalid work order: {error_msg}")
                
        return True
    except Exception as e:
        raise PromptConfigError(f"Configuration validation failed: {str(e)}")
```

## References
- ADR-003: Dependency Injection Patterns
- ADR-004: Model Factory Registration Pattern
- Project Test Guidelines 