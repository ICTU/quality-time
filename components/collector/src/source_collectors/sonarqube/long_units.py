"""SonarQube long units collector."""

from .violations import SonarQubeViolationsWithPercentageScale


class SonarQubeLongUnits(SonarQubeViolationsWithPercentageScale):
    """SonarQube long methods/functions collector."""

    rules_configuration = "long_unit_rules"
    total_metric = "functions"
