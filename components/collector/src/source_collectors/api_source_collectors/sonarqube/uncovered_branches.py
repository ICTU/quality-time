"""SonarQube uncovered branches collector."""

from .base import SonarQubeMetricsBaseClass


class SonarQubeUncoveredBranches(SonarQubeMetricsBaseClass):
    """SonarQube uncovered branches."""

    valueKey = "uncovered_conditions"
    totalKey = "conditions_to_cover"
