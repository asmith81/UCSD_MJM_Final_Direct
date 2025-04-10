"""
Factory for creating output parser instances.

This module provides a factory for creating and configuring output parser instances
based on configuration, following the registration pattern.
"""
from typing import Dict, Type, Optional, Any

from .base_output_parser import BaseOutputParser, OutputParserError
from ..config.base_config import BaseConfig
from ..config.base_config_manager import BaseConfigManager
from ..config.config_types import ConfigType

class OutputParserCreationError(Exception):
    """Raised when output parser creation fails."""
    pass

class OutputParserFactory:
    """
    Factory for creating output parser instances based on configuration.
    Uses registration pattern for adding parser implementations.
    
    Example:
        # Register a parser implementation
        OutputParserFactory.register_parser("json_parser", JsonOutputParser)
        
        # Create a factory instance with config manager
        config_manager = ConfigManager()  # Create your config manager instance
        factory = OutputParserFactory(config_manager)
        
        # Create a parser instance
        parser = factory.create_parser("default_parser")
    """
    
    # Registry of available parser implementations
    PARSER_REGISTRY: Dict[str, Type[BaseOutputParser]] = {}
    
    def __init__(self, config_manager: BaseConfigManager):
        """
        Initialize the factory with required dependencies.
        
        Args:
            config_manager: Configuration manager instance.
            
        Raises:
            ValueError: If config_manager is None
        """
        if config_manager is None:
            raise ValueError("config_manager is required")
        self._config_manager = config_manager
    
    def create_parser(
        self, 
        parser_type: str,
        config: Optional[BaseConfig] = None
    ) -> BaseOutputParser:
        """
        Create and initialize an output parser instance.
        
        Args:
            parser_type: Type of parser to create
            config: Optional explicit configuration
            
        Returns:
            BaseOutputParser: The initialized parser instance
            
        Raises:
            OutputParserCreationError: If parser creation fails
            ValueError: If parser_type is not supported
        """
        try:
            # Validate parser type
            if not parser_type or parser_type not in self.PARSER_REGISTRY:
                raise ValueError(f"Unsupported parser type: {parser_type}")
            
            # Create parser instance
            parser_class = self.PARSER_REGISTRY[parser_type]
            parser = parser_class()
            
            # Initialize if config provided
            if config:
                parser.initialize(config)
                
            return parser
            
        except (ValueError, OutputParserError) as e:
            raise OutputParserCreationError(
                f"Failed to create parser {parser_type}: {str(e)}"
            ) from e
        except Exception as e:
            raise OutputParserCreationError(
                f"Unexpected error creating parser {parser_type}: {str(e)}"
            ) from e
    
    @classmethod
    def register_parser(cls, parser_type: str, parser_class: Type[BaseOutputParser]) -> None:
        """
        Register a new parser implementation.
        
        Args:
            parser_type: Type identifier for the parser
            parser_class: Parser class implementing BaseOutputParser
            
        Raises:
            ValueError: If parser_type is invalid or parser_class doesn't implement BaseOutputParser
        """
        if not parser_type or not isinstance(parser_type, str):
            raise ValueError("Parser type must be a non-empty string")
        
        if not isinstance(parser_class, type) or not issubclass(parser_class, BaseOutputParser):
            raise ValueError("Parser class must implement BaseOutputParser interface")
            
        cls.PARSER_REGISTRY[parser_type] = parser_class 