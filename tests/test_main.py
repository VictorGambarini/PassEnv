import tempfile
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

from typer.testing import CliRunner

from passenv.main import app


class TestCLI:
    def test_load_command_success(self):
        runner = CliRunner()

        with patch("passenv.main.PassEnv") as mock_passenv:
            mock_instance = Mock()
            mock_instance.load.return_value = 'export TEST_VAR="value"'
            mock_passenv.return_value = mock_instance

            result = runner.invoke(app, ["load", "test/path"])

            assert result.exit_code == 0
            assert 'export TEST_VAR="value"' in result.stdout
            mock_instance.load.assert_called_once_with("test/path")

    def test_load_command_error(self):
        runner = CliRunner()

        with patch("passenv.main.PassEnv") as mock_passenv:
            mock_instance = Mock()
            mock_instance.load.side_effect = Exception("Test error")
            mock_passenv.return_value = mock_instance

            result = runner.invoke(app, ["load", "test/path"])

            assert result.exit_code == 1
            assert "Error: Test error" in result.stderr

    def test_unload_command_success(self):
        runner = CliRunner()

        with patch("passenv.main.PassEnv") as mock_passenv:
            mock_instance = Mock()
            mock_instance.unload.return_value = "unset TEST_VAR"
            mock_passenv.return_value = mock_instance

            result = runner.invoke(app, ["unload"])

            assert result.exit_code == 0
            assert "unset TEST_VAR" in result.stdout
            mock_instance.unload.assert_called_once()

    def test_status_command(self):
        runner = CliRunner()

        with patch("passenv.main.PassEnv") as mock_passenv:
            mock_instance = Mock()
            mock_instance.status.return_value = "Environment loaded from 'test/path' (2 variables)"
            mock_passenv.return_value = mock_instance

            result = runner.invoke(app, ["status"])

            assert result.exit_code == 0
            assert "Environment loaded from 'test/path'" in result.stdout
            mock_instance.status.assert_called_once()

    def test_list_command(self):
        runner = CliRunner()

        with patch("passenv.main.PassEnv") as mock_passenv:
            mock_instance = Mock()
            mock_instance.list_entries.return_value = ["database/staging", "api/keys"]
            mock_passenv.return_value = mock_instance

            result = runner.invoke(app, ["list"])

            assert result.exit_code == 0
            assert "database/staging" in result.stdout
            assert "api/keys" in result.stdout
            mock_instance.list_entries.assert_called_once()

    def test_export_command_env_format(self):
        runner = CliRunner()

        with patch("passenv.main.PassEnv") as mock_passenv:
            mock_instance = Mock()
            return_value = "DATABASE_URL=postgres://localhost\nAPI_KEY=secret"
            mock_instance.pass_client.get_entry.return_value = return_value
            mock_instance.parser.parse.return_value = {
                "DATABASE_URL": "postgres://localhost",
                "API_KEY": "secret",
            }
            mock_passenv.return_value = mock_instance

            result = runner.invoke(app, ["export", "test/path"])

            assert result.exit_code == 0
            assert "DATABASE_URL=postgres://localhost" in result.stdout
            assert "API_KEY=secret" in result.stdout

    def test_export_command_yaml_format(self):
        runner = CliRunner()

        with patch("passenv.main.PassEnv") as mock_passenv:
            mock_instance = Mock()
            mock_instance.pass_client.get_entry.return_value = "DATABASE_URL=postgres://localhost"
            mock_instance.parser.parse.return_value = {"DATABASE_URL": "postgres://localhost"}
            mock_passenv.return_value = mock_instance

            result = runner.invoke(app, ["export", "test/path", "--format", "yaml"])

            assert result.exit_code == 0
            assert "DATABASE_URL:" in result.stdout

    def test_export_command_to_file(self):
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test.env"

            with patch("passenv.main.PassEnv") as mock_passenv:
                mock_instance = Mock()
                env = "DATABASE_URL"
                address = "postgres://localhost"
                mock_instance.pass_client.get_entry.return_value = f"{env}={address}"
                mock_instance.parser.parse.return_value = {env: address}
                mock_passenv.return_value = mock_instance

                result = runner.invoke(app, ["export", "test/path", "--output", str(output_file)])

                assert result.exit_code == 0
                assert "Exported 1 variables" in result.stdout
                assert output_file.exists()
                assert "DATABASE_URL=postgres://localhost" in output_file.read_text()

    def test_export_command_error(self):
        runner = CliRunner()

        with patch("passenv.main.PassEnv") as mock_passenv:
            mock_instance = Mock()
            mock_instance.pass_client.get_entry.side_effect = Exception("Test error")
            mock_passenv.return_value = mock_instance

            result = runner.invoke(app, ["export", "test/path"])

            assert result.exit_code == 1
            assert "Error: Test error" in result.stderr

    def test_install_command_basic(self):
        runner = CliRunner()

        with (
            patch("passenv.main._detect_shell_and_rc", return_value=("bash", "/tmp/test_bashrc")),
            patch("passenv.main.install_completion") as mock_install,
            patch("os.path.exists", return_value=False),
            patch("os.makedirs"),
            patch("builtins.open", mock_open()),
        ):

            mock_install.return_value = ("bash", "/tmp/completion")

            result = runner.invoke(app, ["install"])

            assert result.exit_code == 0
            assert "Shell function added" in result.stdout
            assert "completion installed" in result.stdout

    def test_install_command_skip_completion(self):
        runner = CliRunner()

        with (
            patch("passenv.main._detect_shell_and_rc", return_value=("bash", "/tmp/test_bashrc")),
            patch("os.path.exists", return_value=False),
            patch("os.makedirs"),
            patch("builtins.open", mock_open()),
        ):

            result = runner.invoke(app, ["install", "--skip-completion"])

            assert result.exit_code == 0
            assert "Shell function added" in result.stdout
            assert "completion installed" not in result.stdout

    def test_install_command_unsupported_shell(self):
        runner = CliRunner()

        with patch("passenv.main._detect_shell_and_rc", return_value=("unsupported", None)):
            result = runner.invoke(app, ["install"])

            assert result.exit_code == 0
            assert "Unsupported shell" in result.stdout
            assert "Add this function to your shell RC file" in result.stdout

    def test_install_command_completion_error(self):
        runner = CliRunner()

        with (
            patch("passenv.main._detect_shell_and_rc", return_value=("bash", "/tmp/test_bashrc")),
            patch("passenv.main.install_completion", side_effect=Exception("Completion error")),
            patch("os.path.exists", return_value=False),
            patch("os.makedirs"),
            patch("builtins.open", mock_open()),
        ):

            result = runner.invoke(app, ["install"])

            assert result.exit_code == 0
            assert "Could not install completion" in result.stdout

    def test_install_command_fish_shell(self):
        runner = CliRunner()

        with (
            patch("passenv.main._detect_shell_and_rc", return_value=("fish", "/tmp/config.fish")),
            patch("passenv.main.install_completion") as mock_install,
            patch("os.path.exists", return_value=False),
            patch("os.makedirs"),
            patch("builtins.open", mock_open()),
        ):

            mock_install.return_value = ("fish", "/tmp/completion")

            result = runner.invoke(app, ["install"])

            assert result.exit_code == 0
            assert "Restart your shell or run 'source" in result.stdout

    def test_list_command_empty(self):
        runner = CliRunner()

        with patch("passenv.main.PassEnv") as mock_passenv:
            mock_instance = Mock()
            mock_instance.list_entries.return_value = []
            mock_passenv.return_value = mock_instance

            result = runner.invoke(app, ["list"])

            assert result.exit_code == 0
            assert "No pass entries found" in result.stdout
