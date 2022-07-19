"""Data model scales."""

from .meta.scale import Scales


SCALES = Scales.parse_obj(
    dict(
        count=dict(
            name="Count", description="Counts of objects (for example, lines of code, violations, complex units)."
        ),
        percentage=dict(
            name="Percentage",
            description="Percentage of objects (for example, percentage of lines of code not covered by tests, "
            "percentage of violations that are major, percentage of complex units).",
        ),
        version_number=dict(
            name="Version number",
            description="Version numbers of sources (for example, GitLab 10.2, SonarQube 7.4.1, "
            "Quality-time 3.27.1rc-1).",
        ),
    )
)
