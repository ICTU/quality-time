"""SonarQube duplicated lines collector."""

from .base import SonarQubeMetricsBaseClass


class SonarQubeDuplicatedLines(SonarQubeMetricsBaseClass):
    """SonarQube duplicated lines collector."""

    value_key = "duplicated_lines"
    total_key = "lines"
