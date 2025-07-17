import shutil
import subprocess
from typing import List


class PassClient:
    def __init__(self) -> None:
        if not shutil.which("pass"):
            raise RuntimeError("'pass' command not found. Please install pass.")

    def get_entry(self, path: str) -> str:
        try:
            result = subprocess.run(
                ["pass", "show", path], capture_output=True, text=True, check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:
                raise RuntimeError(f"Pass entry '{path}' not found.")
            raise RuntimeError(f"Pass command failed: {e.stderr}")

    def list_entries(self) -> List[str]:
        try:
            result = subprocess.run(["pass", "ls"], capture_output=True, text=True, check=True)
            return self._parse_pass_list(result.stdout)
        except subprocess.CalledProcessError as e:
            if "not a git repository" in e.stderr or "not initialized" in e.stderr:
                raise RuntimeError("Pass store not initialized.")
            raise RuntimeError(f"Pass command failed: {e.stderr}")

    def _parse_pass_list(self, output: str) -> List[str]:
        entries = []
        lines = output.split("\n")

        # First pass: clean all lines and calculate depths
        cleaned_lines = []
        for line in lines:
            if not line or line.strip().startswith("Password Store"):
                continue

            # Remove ANSI color codes
            import re

            clean_line = re.sub(r"\x1b\[[0-9;]*m", "", line)

            # Replace non-breaking spaces with regular spaces
            clean_line = clean_line.replace("\xa0", " ")

            # Calculate depth by counting leading tree characters
            depth = 0
            temp_line = clean_line

            while temp_line:
                if temp_line.startswith("├── ") or temp_line.startswith("└── "):
                    depth += 1
                    temp_line = temp_line[4:]
                elif temp_line.startswith("│   "):
                    depth += 1
                    temp_line = temp_line[4:]
                elif temp_line.startswith("    "):
                    depth += 1
                    temp_line = temp_line[4:]
                else:
                    break

            item_name = temp_line.strip()
            if item_name:
                # Adjust depth to be 0-based (root items are depth 0)
                cleaned_lines.append((depth - 1, item_name))

        # Second pass: build the tree structure
        path_stack: list = []

        for i, (depth, item_name) in enumerate(cleaned_lines):
            # Check if this is a directory by looking at the next line
            is_directory = False
            if i + 1 < len(cleaned_lines):
                next_depth, _ = cleaned_lines[i + 1]
                if next_depth > depth:
                    is_directory = True

            # Adjust path stack to current depth
            # Remove items from stack that are at same or deeper level
            path_stack = path_stack[:depth]

            if is_directory:
                # It's a directory, add to path stack
                path_stack.append(item_name)
            else:
                # It's a password entry
                if path_stack:
                    full_path = "/".join(path_stack + [item_name])
                else:
                    full_path = item_name
                entries.append(full_path)

        return entries
