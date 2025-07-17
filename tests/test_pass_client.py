import subprocess
from unittest.mock import Mock, patch

import pytest

from passenv.pass_client import PassClient


class TestPassClient:
    def test_init_pass_not_found(self):
        with patch("shutil.which", return_value=None):
            with pytest.raises(RuntimeError, match="'pass' command not found"):
                PassClient()

    def test_get_entry_success(self):
        with patch("shutil.which", return_value="/usr/bin/pass"):
            client = PassClient()

            mock_result = Mock()
            mock_result.stdout = "DATABASE_URL=postgres://localhost/test\nAPI_KEY=secret123"

            with patch("subprocess.run", return_value=mock_result) as mock_run:
                result = client.get_entry("test/path")

                assert result == "DATABASE_URL=postgres://localhost/test\nAPI_KEY=secret123"
                mock_run.assert_called_once_with(
                    ["pass", "show", "test/path"], capture_output=True, text=True, check=True
                )

    def test_get_entry_not_found(self):
        with patch("shutil.which", return_value="/usr/bin/pass"):
            client = PassClient()

            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = subprocess.CalledProcessError(1, "pass")

                with pytest.raises(RuntimeError, match="Pass entry 'test/path' not found"):
                    client.get_entry("test/path")

    def test_list_entries_success(self):
        with patch("shutil.which", return_value="/usr/bin/pass"):
            client = PassClient()

            mock_result = Mock()
            mock_result.stdout = """Password Store
├── database
│   ├── staging
│   └── production
└── api
    └── keys"""

            with patch("subprocess.run", return_value=mock_result):
                result = client.list_entries()

                assert "database/staging" in result
                assert "database/production" in result
                assert "api/keys" in result

    def test_list_entries_not_initialized(self):
        with patch("shutil.which", return_value="/usr/bin/pass"):
            client = PassClient()

            with patch("subprocess.run") as mock_run:
                error = subprocess.CalledProcessError(1, "pass")
                error.stderr = "not initialized"
                mock_run.side_effect = error

                with pytest.raises(RuntimeError, match="Pass store not initialized"):
                    client.list_entries()
