import os

import pytest

from passenv.core import PassEnv


class TestPassEnv:
    def test_load_success(self, clean_env, mock_pass_client):
        mock_pass_client.get_entry.return_value = (
            "DATABASE_URL=postgres://localhost/test\nAPI_KEY=secret123"
        )

        passenv = PassEnv()
        result = passenv.load("test/path")

        expected_lines = [
            'export DATABASE_URL="postgres://localhost/test"',
            'export API_KEY="secret123"',
            'export PASSENV_LOADED_VARS="DATABASE_URL,API_KEY"',
            'export PASSENV_SOURCE="test/path"',
        ]

        for line in expected_lines:
            assert line in result

    def test_load_with_existing_environment(self, clean_env, mock_pass_client):
        mock_pass_client.get_entry.return_value = "NEW_VAR=value"

        passenv = PassEnv()
        result = passenv.load("new/path")

        assert 'export NEW_VAR="value"' in result
        assert 'export PASSENV_SOURCE="new/path"' in result

    def test_unload_success(self, clean_env):
        os.environ["PASSENV_LOADED_VARS"] = "DATABASE_URL,API_KEY"
        os.environ["PASSENV_SOURCE"] = "test/path"

        passenv = PassEnv()
        result = passenv.unload()

        expected_lines = [
            "unset DATABASE_URL",
            "unset API_KEY",
            "unset PASSENV_LOADED_VARS",
            "unset PASSENV_SOURCE",
        ]

        for line in expected_lines:
            assert line in result

    def test_unload_nothing_loaded(self, clean_env):
        passenv = PassEnv()

        with pytest.raises(RuntimeError, match="No environment currently loaded"):
            passenv.unload()

    def test_status_loaded(self, clean_env):
        os.environ["PASSENV_LOADED_VARS"] = "DATABASE_URL,API_KEY"
        os.environ["PASSENV_SOURCE"] = "test/path"

        passenv = PassEnv()
        result = passenv.status()

        assert "Environment loaded from 'test/path'" in result
        assert "(2 variables)" in result

    def test_status_not_loaded(self, clean_env):
        passenv = PassEnv()
        result = passenv.status()

        assert result == "No environment currently loaded"

    def test_is_loaded(self, clean_env):
        passenv = PassEnv()

        assert not passenv.is_loaded()

        os.environ["PASSENV_LOADED_VARS"] = "TEST_VAR"
        assert passenv.is_loaded()

    def test_escape_value(self):
        passenv = PassEnv()

        # Test escaping quotes and backslashes
        assert passenv._escape_value("simple") == "simple"
        assert passenv._escape_value('with"quotes') == 'with\\"quotes'
        assert passenv._escape_value("with\\backslash") == "with\\\\backslash"
        assert (
            passenv._escape_value('with"quotes\\and\\backslash')
            == 'with\\"quotes\\\\and\\\\backslash'
        )
