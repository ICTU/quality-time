"""SonarQube many parameters collector."""

from .violations import SonarQubeViolationsWithPercentageScale


class SonarQubeManyParameters(SonarQubeViolationsWithPercentageScale):
    """SonarQube many parameters collector."""

    rules_configuration = "many_parameter_rules"
    total_metric = "functions"
