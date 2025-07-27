import csv
import json
from enum import Enum
from io import StringIO
from typing import Dict

import yaml


class ExportFormat(str, Enum):
    ENV = "env"
    YAML = "yaml"
    JSON = "json"
    CSV = "csv"
    DOCKER = "docker"


class Exporter:
    """Handle exporting environment variables to different formats"""

    def __init__(self) -> None:
        self.formatters = {
            ExportFormat.ENV: self._format_env,
            ExportFormat.YAML: self._format_yaml,
            ExportFormat.JSON: self._format_json,
            ExportFormat.CSV: self._format_csv,
            ExportFormat.DOCKER: self._format_docker,
        }

    def export(self, variables: Dict[str, str], format: ExportFormat) -> str:
        """Export variables to the specified format"""
        if format not in self.formatters:
            raise ValueError(f"Unsupported export format: {format}")

        return self.formatters[format](variables)

    def _format_env(self, variables: Dict[str, str]) -> str:
        """Export as .env format"""
        lines = []
        for key, value in variables.items():
            # Quote values that contain spaces or special characters
            if " " in value or '"' in value or "'" in value or "\n" in value:
                # Escape quotes and wrap in double quotes
                escaped_value = value.replace("\\", "\\\\").replace('"', '\\"')
                lines.append(f'{key}="{escaped_value}"')
            else:
                lines.append(f"{key}={value}")
        return "\n".join(lines)

    def _format_yaml(self, variables: Dict[str, str]) -> str:
        """Export as YAML format"""
        try:
            return yaml.dump(variables, default_flow_style=False, allow_unicode=True)
        except NameError:
            # Fallback if PyYAML not installed
            lines = []
            for key, value in variables.items():
                # Simple YAML formatting
                if isinstance(value, str) and (
                    ":" in value or "#" in value or value.startswith(" ") or value.endswith(" ")
                ):
                    lines.append(f'{key}: "{value}"')
                else:
                    lines.append(f"{key}: {value}")
            return "\n".join(lines)

    def _format_json(self, variables: Dict[str, str]) -> str:
        """Export as JSON format"""
        return json.dumps(variables, indent=2, ensure_ascii=False)

    def _format_csv(self, variables: Dict[str, str]) -> str:
        """Export as CSV format with KEY,VALUE columns"""
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["KEY", "VALUE"])
        for key, value in variables.items():
            writer.writerow([key, value])
        return output.getvalue()

    def _format_docker(self, variables: Dict[str, str]) -> str:
        """Export as Docker environment arguments"""
        args = []
        for key, value in variables.items():
            # Escape quotes for shell
            escaped_value = value.replace("\\", "\\\\").replace('"', '\\"')
            args.append(f'-e {key}="{escaped_value}"')
        return " ".join(args)
