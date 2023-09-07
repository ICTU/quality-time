"""Data model scales."""

from .meta.scale import Scale

SCALES = {
    "count": Scale(
        name="Count",
        description="Counts of objects (for example, lines of code, violations, complex units).",
    ),
    "percentage": Scale(
        name="Percentage",
        description="Percentage of objects (for example, percentage of lines of code not covered by tests, "
        "percentage of violations that are major, percentage of complex units).",
    ),
    "version_number": Scale(
        name="Version number",
        description="Version numbers of sources (for example, GitLab 10.2, SonarQube 7.4.1, "
        "Quality-time 3.27.1rc-1).",
    ),
}
