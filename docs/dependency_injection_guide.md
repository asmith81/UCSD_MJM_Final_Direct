# Dependency Injection Guide

## Overview

This document explains the dependency injection approach used throughout the codebase, focusing on factory classes. Proper dependency injection improves testability, maintainability, and adheres to our core architectural principles.

## Factory Classes and Dependencies

Factory classes in our codebase follow the dependency injection pattern. This means all dependencies are provided explicitly rather than being accessed through global state or singletons.

### Key Changes

We have updated factory classes to require explicit configuration manager injection:

- `ModelFactory`
- `OutputParserFactory`
- `PromptFactory`
- `EvaluationService`

## Correct Usage

### Before (Deprecated)

```python
# DO NOT USE this approach anymore
from src.models import ModelFactory

# This implicitly relies on global initialization
factory = ModelFactory()  # ❌ WRONG
```

### After (Correct)

```python
from src.models import ModelFactory
from src.config import get_config_manager

# Explicitly inject the configuration manager
config_manager = get_config_manager()
factory = ModelFactory(config_manager)  # ✅ CORRECT
```

## Migration Guide

If you have code that uses factory classes, update it as follows:

1. Import the configuration manager:
   ```python
   from src.config import get_config_manager
   ```

2. Get an instance of the configuration manager:
   ```python
   config_manager = get_config_manager()
   ```

3. Pass the configuration manager to the factory constructor:
   ```python
   factory = ModelFactory(config_manager)
   ```

## Dependency Injection for Testing

In tests, use mocks to inject dependencies:

```python
from unittest.mock import Mock

# Create mock dependencies
mock_config_manager = Mock()

# Configure the mock if needed
mock_config_manager.get_config.return_value = mock_config

# Inject the mock
factory = ModelFactory(mock_config_manager)
```

## Benefits

This approach provides several benefits:

1. **Testability**: Dependencies can be easily mocked in tests
2. **Explicitness**: Dependencies are visible in the code
3. **Flexibility**: Implementation details can be changed without affecting clients
4. **Decoupling**: Components are not tightly coupled to global state

## Core Architectural Principles

This approach aligns with our core architectural principles:

1. **Dependency Injection**: "Dependencies should be passed explicitly to constructors"
2. **Explicit over Implicit**: "Favor explicit over implicit code"
3. **Interface-Based Design**: "Depend on abstractions, not concrete implementations"
4. **Separation of Concerns**: "Components should be able to evolve independently" 