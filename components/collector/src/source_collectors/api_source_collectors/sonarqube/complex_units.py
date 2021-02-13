"""SonarQube complex units collector."""

from .violations import SonarQubeViolationsWithPercentageScale


class SonarQubeComplexUnits(SonarQubeViolationsWithPercentageScale):
    """SonarQube complex methods/functions collector."""

    rules_configuration = "complex_unit_rules"
    total_metric = "functions"
