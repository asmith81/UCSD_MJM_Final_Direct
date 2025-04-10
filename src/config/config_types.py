"""
Configuration type definitions.

This module defines the available configuration types in the system.
"""
from enum import Enum, auto


class ConfigType(Enum):
    """
    Enumeration of configuration types.
    
    This enum defines the different types of configurations that can be loaded
    and managed by the configuration system.
    """
    MODEL = auto()      # Model-specific configurations
    PROMPT = auto()     # Prompt template configurations
    EVALUATION = auto() # Evaluation metric configurations 