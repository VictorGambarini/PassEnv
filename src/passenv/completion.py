from typing import List

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
