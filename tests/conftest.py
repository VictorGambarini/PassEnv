import os
import shutil
import tempfile
from unittest.mock import patch

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_pass_client():
    """Mock PassClient for testing"""
    with patch("passenv.core.PassClient") as mock_client:
        yield mock_client.return_value


@pytest.fixture
def clean_env():
    """Clean environment for testing"""
    env_vars = ["PASSENV_LOADED_VARS", "PASSENV_SOURCE", "TEST_VAR", "DATABASE_URL"]
    original_values = {}

    # Save original values
    for var in env_vars:
        original_values[var] = os.environ.get(var)
        if var in os.environ:
            del os.environ[var]

    yield

    # Restore original values
    for var, value in original_values.items():
        if value is not None:
            os.environ[var] = value
        elif var in os.environ:
            del os.environ[var]
