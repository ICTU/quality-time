"""Changelog parsing."""


def _find_version_index(lines: list[str], version: str) -> int | None:
    """Return the index of the line that introduces the version's changes, or None when absent.

    Prefer a heading line (starting with '#') that mentions the version, so that a prose mention of the
    version inside another version's section (e.g. "shipped in 0.10.0") doesn't anchor parsing in the
    wrong place. Fall back to the first line mentioning the version when no heading does.
    """
    fallback = None
    for index, line in enumerate(lines):
        if version in line:
            if line.startswith("#"):
                return index
            if fallback is None:
                fallback = index
    return fallback


def get_version_changes_from_changelog(text: str, version: str, max_length: int = 20) -> str:
    """Return the changes for the version from the changelog. Default to the first max length lines."""
    all_lines = text.splitlines()
    start = _find_version_index(all_lines, version)
    previous_version_found = False
    if start is None:
        lines = all_lines
    else:
        lines = [all_lines[start]]
        for line in all_lines[start + 1 :]:
            if line.startswith("## ") and version not in line:
                previous_version_found = True
                break
            lines.append(line)
    if lines and not lines[-1].strip():
        lines = lines[:-1]  # Remove empty last line
    if len(lines) > max_length and not previous_version_found:
        lines = [*lines[:max_length], "..."]  # Add ellipsis if too many lines
    return "\n".join(lines)
