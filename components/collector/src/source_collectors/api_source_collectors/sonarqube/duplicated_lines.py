"""SonarQube duplicated lines collector."""

from .base import SonarQubeMetricsBaseClass


class SonarQubeDuplicatedLines(SonarQubeMetricsBaseClass):
    """SonarQube duplicated lines collector."""

    valueKey = "duplicated_lines"
    totalKey = "lines"
