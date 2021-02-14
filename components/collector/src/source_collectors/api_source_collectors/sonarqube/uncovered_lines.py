"""SonarQube uncovered lines collector."""

from .base import SonarQubeMetricsBaseClass


class SonarQubeUncoveredLines(SonarQubeMetricsBaseClass):
    """SonarQube uncovered lines of code."""

    valueKey = "uncovered_lines"
    totalKey = "lines_to_cover"
