import pytest
import tempfile
import shutil
import os
from pathlib import Path

@pytest.fixture(scope="session")
def temp_config_dir():
    """Create a temporary directory with test config files."""
    temp_dir = tempfile.mkdtemp()
    
    # Copy test fixtures to temp directory
    fixture_dir = Path(__file__).parent / "fixtures" / "config"
    for root, _, files in os.walk(fixture_dir):
        for file in files:
            if file.endswith('.yaml'):
                src = os.path.join(root, file)
                dst = os.path.join(temp_dir, file)
                shutil.copy2(src, dst)
    
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def config_factory():
    """Create a config factory for testing."""
    from src.config.config_factory import ConfigFactory
    return ConfigFactory()

@pytest.fixture
def config_loader(temp_config_dir, config_factory):
    """Create a config loader with test fixtures."""
    from src.config.config_loader import ConfigLoader
    return ConfigLoader(temp_config_dir, config_factory) 