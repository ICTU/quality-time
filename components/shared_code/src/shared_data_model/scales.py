"""Data model scales."""

from .meta.scale import Scale

VERSION_NUMBER_EXPLANATION = """Quality-time uses the packaging library (1) to parse version numbers. The packaging
library expects version numbers to comply with PEP-440 (2). PEP is an abbreviation for Python Enhancement Proposal,
but this PEP is primarily a standard for version numbers. PEP-440 encompasses most of the semantic versioning scheme
(3) so version numbers that follow semantic versioning are usually parsed correctly."""
VERSION_NUMBER_EXPLANATION_URLS = [
    "https://pypi.org/project/packaging/",
    "https://peps.python.org/pep-0440/",
    "https://semver.org",
]

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
        description="Version numbers of sources (for example, GitLab 10.2, SonarQube 7.4.1, Quality-time 3.27.1rc-1).",
    ),
}
