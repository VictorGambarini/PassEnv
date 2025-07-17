import os
from typing import List

from .parser import EnvParser
from .pass_client import PassClient


class PassEnv:
    LOADED_VARS_KEY = "PASSENV_LOADED_VARS"
    SOURCE_KEY = "PASSENV_SOURCE"

    def __init__(self) -> None:
        self.pass_client = PassClient()
        self.parser = EnvParser()

    def load(self, pass_path: str) -> str:
        commands = []

        # If something is already loaded, unload it first
        if self.is_loaded():
            loaded_vars = os.environ.get(self.LOADED_VARS_KEY, "").split(",")
            for var in loaded_vars:
                if var.strip():
                    commands.append(f"unset {var.strip()}")

        # Get content from pass
        content = self.pass_client.get_entry(pass_path)

        # Parse environment variables
        variables = self.parser.parse(content)

        # Generate shell export commands
        commands = []
        var_names = []

        for key, value in variables.items():
            commands.append(f'export {key}="{self._escape_value(value)}"')
            var_names.append(key)

        # Add tracking variables
        commands.append(f'export {self.LOADED_VARS_KEY}="{",".join(var_names)}"')
        commands.append(f'export {self.SOURCE_KEY}="{pass_path}"')

        return "\n".join(commands)

    def unload(self) -> str:
        if not self.is_loaded():
            raise RuntimeError("No environment currently loaded")

        loaded_vars = os.environ.get(self.LOADED_VARS_KEY, "").split(",")
        commands = []

        # Unset all loaded variables
        for var in loaded_vars:
            if var.strip():
                commands.append(f"unset {var.strip()}")

        # Unset tracking variables
        commands.append(f"unset {self.LOADED_VARS_KEY}")
        commands.append(f"unset {self.SOURCE_KEY}")

        return "\n".join(commands)

    def status(self) -> str:
        if not self.is_loaded():
            return "No environment currently loaded"

        source = os.environ.get(self.SOURCE_KEY, "unknown")
        loaded_vars = os.environ.get(self.LOADED_VARS_KEY, "").split(",")
        var_count = len([v for v in loaded_vars if v.strip()])

        return f"Environment loaded from '{source}' ({var_count} variables)"

    def list_entries(self) -> List[str]:
        return self.pass_client.list_entries()

    def is_loaded(self) -> bool:
        return self.LOADED_VARS_KEY in os.environ

    def _escape_value(self, value: str) -> str:
        # Escape double quotes and backslashes for shell
        return value.replace("\\", "\\\\").replace('"', '\\"')
