"""SonarQube uncovered lines collector."""

from .base import SonarQubeMetricsBaseClass


class SonarQubeUncoveredLines(SonarQubeMetricsBaseClass):
    """SonarQube uncovered lines of code."""

    value_key = "uncovered_lines"
    total_key = "lines_to_cover"
