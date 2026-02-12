"""
Pytest configuration for survey_analyzer package.

Handles src/ layout by adding the src directory to Python path.
"""

import sys
import pytest
from pathlib import Path


def pytest_configure(config):
    """
    Configure pytest to find survey_analyzer module.

    The package uses src/ layout, so we need to add src/ to sys.path.
    """
    # Get the tests directory
    tests_dir = Path(__file__).parent
    # Get the package root (tests/parent)
    package_root = tests_dir.parent
    # Add src directory to path
    src_dir = package_root / "src"
    sys.path.insert(0, str(src_dir))


@pytest.fixture
def sample_data_dir():
    """Path to sample data directory."""
    return Path(__file__).parent.parent / "data"


@pytest.fixture
def sample_sav_file(sample_data_dir):
    """Path to a sample .sav file for testing."""
    sav_file = sample_data_dir / "simple-data.sav"
    if sav_file.exists():
        return str(sav_file)
    pytest.skip(f"Sample .sav file not found: {sav_file}")
