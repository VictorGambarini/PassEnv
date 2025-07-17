import re
from typing import Dict


class EnvParser:
    VAR_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

    def parse(self, content: str) -> Dict[str, str]:
        variables = {}
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Check for key=value format
            if "=" not in line:
                raise ValueError(f"Invalid line {line_num}: '{line}' - missing '='")

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            # Validate variable name
            if not self.VAR_NAME_PATTERN.match(key):
                raise ValueError(f"Invalid variable name '{key}' on line {line_num}")

            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]

            variables[key] = value

        if not variables:
            raise ValueError("Pass entry contains no valid environment variables")

        return variables

    def validate_variables(self, variables: Dict[str, str]) -> None:
        for key, value in variables.items():
            if not self.VAR_NAME_PATTERN.match(key):
                raise ValueError(f"Invalid variable name: '{key}'")
