from unittest.mock import patch

import pytest

from passenv.exporters import Exporter, ExportFormat


class TestExporter:
    def test_export_env_format(self):
        exporter = Exporter()
        variables = {
            "DATABASE_URL": "postgres://localhost/test",
            "API_KEY": "secret123",
            "DEBUG": "true",
        }

        result = exporter.export(variables, ExportFormat.ENV)

        assert "DATABASE_URL=postgres://localhost/test" in result
        assert "API_KEY=secret123" in result
        assert "DEBUG=true" in result

    def test_export_env_format_with_spaces(self):
        exporter = Exporter()
        variables = {"MESSAGE": "Hello World", "PATH_WITH_SPACES": "/path with spaces/file"}

        result = exporter.export(variables, ExportFormat.ENV)

        assert 'MESSAGE="Hello World"' in result
        assert 'PATH_WITH_SPACES="/path with spaces/file"' in result

    def test_export_env_format_with_quotes(self):
        exporter = Exporter()
        variables = {"MESSAGE": 'Hello "World"', "ESCAPED": "back\\slash"}

        result = exporter.export(variables, ExportFormat.ENV)
        print(f"*****Result: {result}")

        assert 'MESSAGE="Hello \\"World\\""' in result
        assert "ESCAPED=back\\slash" in result

    def test_export_yaml_format(self):
        exporter = Exporter()
        variables = {"DATABASE_URL": "postgres://localhost/test", "API_KEY": "secret123"}

        result = exporter.export(variables, ExportFormat.YAML)

        assert "DATABASE_URL:" in result
        assert "API_KEY:" in result

    def test_export_yaml_format_fallback(self):
        """Test YAML export without PyYAML installed"""
        exporter = Exporter()
        variables = {"DATABASE_URL": "postgres://localhost/test", "SPECIAL": "value:with:colons"}

        # Mock yaml.dump to raise NameError (simulating missing PyYAML)
        with patch("passenv.exporters.yaml.dump", side_effect=NameError()):
            result = exporter.export(variables, ExportFormat.YAML)

            # The fallback code correctly quotes values with colons (YAML special chars)
            assert 'DATABASE_URL: "postgres://localhost/test"' in result
            assert 'SPECIAL: "value:with:colons"' in result

    def test_export_json_format(self):
        exporter = Exporter()
        variables = {"DATABASE_URL": "postgres://localhost/test", "API_KEY": "secret123"}

        result = exporter.export(variables, ExportFormat.JSON)

        assert '"DATABASE_URL": "postgres://localhost/test"' in result
        assert '"API_KEY": "secret123"' in result

    def test_export_csv_format(self):
        exporter = Exporter()
        variables = {"DATABASE_URL": "postgres://localhost/test", "API_KEY": "secret123"}

        result = exporter.export(variables, ExportFormat.CSV)

        assert "KEY,VALUE" in result
        assert "DATABASE_URL,postgres://localhost/test" in result
        assert "API_KEY,secret123" in result

    def test_export_docker_format(self):
        exporter = Exporter()
        variables = {"DATABASE_URL": "postgres://localhost/test", "API_KEY": "secret123"}

        result = exporter.export(variables, ExportFormat.DOCKER)

        assert '-e DATABASE_URL="postgres://localhost/test"' in result
        assert '-e API_KEY="secret123"' in result

    def test_export_docker_format_with_quotes(self):
        exporter = Exporter()
        variables = {"MESSAGE": 'Hello "World"', "ESCAPED": "back\\slash"}

        result = exporter.export(variables, ExportFormat.DOCKER)

        assert '-e MESSAGE="Hello \\"World\\""' in result
        assert '-e ESCAPED="back\\\\slash"' in result

    def test_export_unsupported_format(self):
        exporter = Exporter()
        variables = {"TEST": "value"}

        with pytest.raises(ValueError, match="Unsupported export format"):
            exporter.export(variables, "unsupported")
