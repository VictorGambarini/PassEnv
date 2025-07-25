import os
from typing import List, Tuple

from shellingham import detect_shell  # type: ignore

from .pass_client import PassClient


def complete_pass_entries(incomplete: str) -> List[str]:
    """Auto-complete pass entries"""
    try:
        client = PassClient()
        entries = client.list_entries()

        # Filter entries that start with the incomplete string
        matches = [entry for entry in entries if entry.startswith(incomplete)]
        return matches
    except Exception:
        # If pass fails, return empty list
        return []


def _detect_shell_and_rc() -> Tuple[str, str | None]:
    """Detect shell using Typer's logic and return shell name and RC file path"""
    try:
        shell, shell_path = detect_shell()
    except Exception:
        # Fallback if shellingham fails
        shell = os.environ.get("SHELL", "").split("/")[-1]

    # Map shell to RC file
    rc_files = {
        "bash": "~/.bashrc",
        "zsh": "~/.zshrc",
        "fish": "~/.config/fish/config.fish",
        "tcsh": "~/.tcshrc",
        "csh": "~/.cshrc",
    }

    rc_file = rc_files.get(shell)
    if rc_file:
        rc_file = os.path.expanduser(rc_file)

    return shell, rc_file
