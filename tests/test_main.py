from unittest.mock import Mock, patch

from typer.testing import CliRunner

from passenv.main import app


class TestCLI:
    def test_load_command_success(self):
        runner = CliRunner()

        with patch("passenv.main.PassEnv") as mock_passenv:
            mock_instance = Mock()
            mock_instance.load.return_value = 'export TEST_VAR="value"'
            mock_passenv.return_value = mock_instance

            result = runner.invoke(app, ["load", "test/path"], mix_stderr=False)

            assert result.exit_code == 0
            assert 'export TEST_VAR="value"' in result.stdout
            mock_instance.load.assert_called_once_with("test/path")

    def test_load_command_error(self):
        runner = CliRunner()

        with patch("passenv.main.PassEnv") as mock_passenv:
            mock_instance = Mock()
            mock_instance.load.side_effect = Exception("Test error")
            mock_passenv.return_value = mock_instance

            result = runner.invoke(app, ["load", "test/path"], mix_stderr=False)

            assert result.exit_code == 1
            assert "Error: Test error" in result.stderr

    def test_unload_command_success(self):
        runner = CliRunner()

        with patch("passenv.main.PassEnv") as mock_passenv:
            mock_instance = Mock()
            mock_instance.unload.return_value = "unset TEST_VAR"
            mock_passenv.return_value = mock_instance

            result = runner.invoke(app, ["unload"], mix_stderr=False)

            assert result.exit_code == 0
            assert "unset TEST_VAR" in result.stdout
            mock_instance.unload.assert_called_once()

    def test_status_command(self):
        runner = CliRunner()

        with patch("passenv.main.PassEnv") as mock_passenv:
            mock_instance = Mock()
            mock_instance.status.return_value = "Environment loaded from 'test/path' (2 variables)"
            mock_passenv.return_value = mock_instance

            result = runner.invoke(app, ["status"], mix_stderr=False)

            assert result.exit_code == 0
            assert "Environment loaded from 'test/path'" in result.stdout
            mock_instance.status.assert_called_once()

    def test_list_command(self):
        runner = CliRunner()

        with patch("passenv.main.PassEnv") as mock_passenv:
            mock_instance = Mock()
            mock_instance.list_entries.return_value = ["database/staging", "api/keys"]
            mock_passenv.return_value = mock_instance

            result = runner.invoke(app, ["list"], mix_stderr=False)

            assert result.exit_code == 0
            assert "database/staging" in result.stdout
            assert "api/keys" in result.stdout
            mock_instance.list_entries.assert_called_once()
