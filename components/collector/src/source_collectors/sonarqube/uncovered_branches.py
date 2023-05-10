"""SonarQube uncovered branches collector."""

from .base import SonarQubeMetricsBaseClass


class SonarQubeUncoveredBranches(SonarQubeMetricsBaseClass):
    """SonarQube uncovered branches."""

    value_key = "uncovered_conditions"
    total_key = "conditions_to_cover"
