# 006. Model Configuration Validation Utilities

## Status

Proposed

## Context

Model configuration validation is a critical aspect of our system. Currently, each model implements its own validation logic through the `validate_config` method in the `BaseModel` interface. This approach has led to several issues:

1. **Inconsistent Validation**: Different model implementations validate configurations differently
2. **Duplicate Code**: Common validation logic is replicated across models
3. **Limited Reusability**: Validation utilities cannot be easily shared
4. **Testing Challenges**: Difficult to test validation logic separately from models
5. **Error Reporting**: Inconsistent error messages and handling

Recent test failures highlighted these issues when we discovered that model validation errors were being directly propagated as `ModelConfigError` rather than being wrapped in `ModelCreationError`. While this specific exception handling is correct (preserving error specificity), it points to a broader need for a more structured approach to configuration validation.

## Decision

We will implement a dedicated Model Configuration Validation Utilities system with these key components:

1. **ValidationResult Class**:
```python
class ValidationResult:
    def __init__(self, is_valid: bool, errors: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        
    def add_error(self, error: str) -> None:
        self.errors.append(error)
        self.is_valid = False
        
    def merge(self, other: 'ValidationResult') -> 'ValidationResult':
        if self.is_valid and other.is_valid:
            return ValidationResult(True)
        
        result = ValidationResult(False)
        result.errors.extend(self.errors)
        result.errors.extend(other.errors)
        return result
```

2. **ModelConfigValidator Interface**:
```python
class ModelConfigValidator(ABC):
    @abstractmethod
    def validate(self, config: BaseConfig) -> ValidationResult:
        """
        Validate the configuration.
        
        Args:
            config: The configuration to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        pass
```

3. **Common Validators**:
```python
class RequiredFieldValidator(ModelConfigValidator):
    def __init__(self, required_fields: List[str]):
        self.required_fields = required_fields
        
    def validate(self, config: BaseConfig) -> ValidationResult:
        result = ValidationResult(True)
        for field in self.required_fields:
            if not config.has_value(field):
                result.add_error(f"Missing required field: {field}")
        return result

class TypeValidator(ModelConfigValidator):
    def __init__(self, field: str, expected_type: type):
        self.field = field
        self.expected_type = expected_type
        
    def validate(self, config: BaseConfig) -> ValidationResult:
        result = ValidationResult(True)
        value = config.get_value(self.field)
        if value is not None and not isinstance(value, self.expected_type):
            result.add_error(f"Field {self.field} must be of type {self.expected_type.__name__}")
        return result
```

4. **Composite Validator**:
```python
class CompositeValidator(ModelConfigValidator):
    def __init__(self, validators: List[ModelConfigValidator]):
        self.validators = validators
        
    def validate(self, config: BaseConfig) -> ValidationResult:
        result = ValidationResult(True)
        for validator in self.validators:
            result = result.merge(validator.validate(config))
        return result
```

5. **Integration with Models**:
```python
class BaseModelImpl(BaseModel):
    def __init__(self):
        self._validator = self._create_validator()
        
    def _create_validator(self) -> ModelConfigValidator:
        """
        Create a validator for this model's configuration.
        Override in subclasses to provide model-specific validation.
        """
        return CompositeValidator([
            RequiredFieldValidator(["type", "version"]),
            TypeValidator("version", str)
        ])
        
    def validate_config(self, config: BaseConfig) -> bool:
        result = self._validator.validate(config)
        if not result.is_valid:
            self.validation_errors = result.errors
            return False
        return True
```

## Rationale

This approach offers several benefits:

1. **Reusable Validation Logic**: Common validation patterns can be encapsulated in reusable validators
2. **Composable Validation**: Validators can be combined for complex validation rules
3. **Testable Components**: Validators can be tested independently from models
4. **Consistent Error Reporting**: Standardized validation results with detailed error messages
5. **Separation of Concerns**: Validation logic is separated from model implementation
6. **Extensibility**: New validators can be added without modifying existing code
7. **Configuration-Specific Validation**: Each model can still define its specific validation requirements

## Consequences

### Positive

- Reduced duplication of validation code
- More consistent error reporting
- Better testability of validation logic
- Clearer separation of validation from model implementation
- Enables more sophisticated validation patterns
- Consistent handling of configuration errors

### Negative

- Additional abstraction layer
- Slight increase in code complexity
- Migration effort for existing models

### Neutral

- Models still need to define their validation requirements
- Exception handling approach remains the same
- Integration with existing factory system

## Implementation Guidelines

1. **Validation Component Organization**:
   - Place validators in `src/models/validation/`
   - Create common validators for widely used patterns
   - Document each validator's purpose and usage

2. **Exception Handling**:
   - Maintain the current approach of preserving specific error types
   - `ModelConfigError` should continue to be used for validation failures
   - Include validation result errors in exception messages

3. **Integration with Model Factory**:
   - Factory continues to call `validate_config` on models
   - Validation errors continue to propagate as `ModelConfigError`
   - No changes needed to factory error handling logic

4. **Testing Recommendations**:
   - Test validators independently from models
   - Create test cases for common validation patterns
   - Ensure validation errors are properly captured and reported

5. **Documentation**:
   - Document available validators
   - Provide examples of validation composition
   - Update model implementation guide

## References

- [Core Architectural Principles](../rules/core-architectural-principals.mdc)
- [ADR 003: Dependency Injection Patterns](./003-dependency-injection-patterns.md)
- [ADR 004: Model Factory Registration Pattern](./004-model-factory-registration.md)
- [ADR 005: Required Dependency Injection for Factory Classes](./005-factory-required-dependency-injection.md) 