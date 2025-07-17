import pytest

from passenv.parser import EnvParser


class TestEnvParser:
    def test_parse_simple_variables(self):
        parser = EnvParser()
        content = """
DATABASE_URL=postgres://localhost/test
API_KEY=secret123
DEBUG=true
        """
        result = parser.parse(content)

        assert result == {
            "DATABASE_URL": "postgres://localhost/test",
            "API_KEY": "secret123",
            "DEBUG": "true",
        }

    def test_parse_with_comments(self):
        parser = EnvParser()
        content = """
# Database configuration
DATABASE_URL=postgres://localhost/test
# API settings
API_KEY=secret123
        """
        result = parser.parse(content)

        assert result == {"DATABASE_URL": "postgres://localhost/test", "API_KEY": "secret123"}

    def test_parse_with_quotes(self):
        parser = EnvParser()
        content = """
DATABASE_URL="postgres://localhost/test"
API_KEY='secret123'
MESSAGE="Hello, World!"
        """
        result = parser.parse(content)

        assert result == {
            "DATABASE_URL": "postgres://localhost/test",
            "API_KEY": "secret123",
            "MESSAGE": "Hello, World!",
        }

    def test_parse_with_empty_lines(self):
        parser = EnvParser()
        content = """
DATABASE_URL=postgres://localhost/test

API_KEY=secret123

        """
        result = parser.parse(content)

        assert result == {"DATABASE_URL": "postgres://localhost/test", "API_KEY": "secret123"}

    def test_parse_with_spaces_around_equals(self):
        parser = EnvParser()
        content = """
DATABASE_URL = postgres://localhost/test
API_KEY =secret123
DEBUG= true
        """
        result = parser.parse(content)

        assert result == {
            "DATABASE_URL": "postgres://localhost/test",
            "API_KEY": "secret123",
            "DEBUG": "true",
        }

    def test_parse_invalid_variable_name(self):
        parser = EnvParser()
        content = "123INVALID=value"

        with pytest.raises(ValueError, match="Invalid variable name"):
            parser.parse(content)

    def test_parse_missing_equals(self):
        parser = EnvParser()
        content = "INVALID_LINE"

        with pytest.raises(ValueError, match="missing '='"):
            parser.parse(content)

    def test_parse_empty_content(self):
        parser = EnvParser()
        content = """
# Just comments
# Nothing else
        """

        with pytest.raises(ValueError, match="no valid environment variables"):
            parser.parse(content)

    def test_parse_value_with_equals(self):
        parser = EnvParser()
        content = "DATABASE_URL=postgres://user:pass=word@localhost/db"

        result = parser.parse(content)
        assert result["DATABASE_URL"] == "postgres://user:pass=word@localhost/db"
