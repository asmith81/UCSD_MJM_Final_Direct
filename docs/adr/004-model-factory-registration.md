# 004. Model Factory Registration Pattern

## Status

Proposed

## Context

The ModelFactory is a critical component responsible for creating model instances in the system. Initially, it was implemented with hardcoded model implementations:

```python
class ModelFactory:
    MODEL_REGISTRY: Dict[str, Type[BaseModel]] = {
        "doctr": DoctrModel,
        "llama_vision": LlamaVisionModel,
        "pixtral": PixtralModel
    }
```

This approach presents several issues:
1. Tight coupling between the factory and specific model implementations
2. Violation of the Open/Closed Principle when adding new models
3. Difficulty in testing due to required concrete implementations
4. Inflexibility in dynamic model loading and configuration

## Decision

We will implement a dynamic registration pattern for the ModelFactory with these key features:

1. Empty Initial Registry:
```python
class ModelFactory:
    MODEL_REGISTRY: Dict[str, Type[BaseModel]] = {}
```

2. Registration Method:
```python
@classmethod
def register_model(cls, model_type: str, model_class: Type[BaseModel]) -> None:
    if not model_type or not isinstance(model_type, str):
        raise ValueError("Model type must be a non-empty string")
    if not isinstance(model_class, type) or not issubclass(model_class, BaseModel):
        raise ValueError("Model class must implement BaseModel interface")
    cls.MODEL_REGISTRY[model_type] = model_class
```

3. Dynamic Model Creation:
```python
def create_model(self, model_name: str, model_config: Optional[BaseConfig] = None) -> BaseModel:
    config = model_config or self._load_model_config(model_name)
    model_type = config.get_value("type")
    if model_type not in self.MODEL_REGISTRY:
        raise ModelCreationError(f"Unsupported model type: {model_type}")
    return self.MODEL_REGISTRY[model_type]()
```

## Rationale

This decision aligns with several architectural principles:

1. **Dependency Injection Pattern**
   - Follows ADR-003 guidelines for dependency management
   - Enables constructor-based injection for models
   - Maintains clear separation of concerns

2. **Interface-Based Design**
   - Models depend on the BaseModel interface
   - Factory depends on abstractions, not implementations
   - Enables easy testing and mocking

3. **Open/Closed Principle**
   - New models can be added without modifying factory code
   - Registration pattern supports extensibility
   - Maintains system stability when adding models

4. **Testing and Maintainability**
   - Easy to create mock models for testing
   - No need for concrete implementations during testing
   - Clear registration process for new models

## Consequences

### Positive

- Decoupled factory from specific model implementations
- Easier testing with mock models
- Support for dynamic model loading
- Clear path for adding new models
- Better adherence to SOLID principles

### Negative

- Need to explicitly register models
- Slightly more complex initialization process
- Potential for runtime errors if models aren't registered

### Neutral

- Registration must happen before model creation
- Need to document registration process
- May need startup configuration for model registration

## Implementation Guidelines

1. **Model Registration**
   - Register models during system initialization
   - Validate model implementations at registration time
   - Document registration requirements

2. **Error Handling**
   - Clear error messages for registration failures
   - Validation of model types and implementations
   - Runtime checks for unregistered models

3. **Configuration**
   - Support for model-specific configuration
   - Validation of configuration at creation time
   - Clear documentation of configuration requirements

4. **Testing**
   - Provide mock models for testing
   - Test registration edge cases
   - Verify error handling

## Next Steps

1. Update ModelFactory implementation to use registration pattern
2. Create documentation for model registration process
3. Update existing model implementations to use registration
4. Add comprehensive tests for registration pattern
5. Review and update related components (e.g., configuration handling) 