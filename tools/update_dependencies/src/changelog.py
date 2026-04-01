"""Changelog parsing."""


def get_version_changes_from_changelog(text: str, version: str, max_length: int = 20) -> str:
    """Return the changes for the version from the changelog. Default to the first max length lines."""
    lines = []
    version_found = False
    previous_version_found = False
    for line in text.splitlines():
        if version in line:
            version_found = True
        elif version_found and line.startswith("## "):
            previous_version_found = True
            break
        if version_found:
            lines.append(line)
    if not version_found:
        lines = text.splitlines()
    if lines and not lines[-1].strip():
        lines = lines[:-1]  # Remove empty last line
    if len(lines) > max_length and not previous_version_found:
        lines = [*lines[:max_length], "..."]  # Add ellipsis if too many lines
    return "\n".join(lines)
