"""SonarQube commented-out-code collector."""

from .violations import SonarQubeViolations


class SonarQubeCommentedOutCode(SonarQubeViolations):
    """SonarQube commented out code collector."""

    # Unfortunately, the SonarQube API for commented out code doesn't seem to return the number of lines commented out,
    # so we can't compute a percentage of commented out code. And hence this collector is not a subclass of
    # SonarQubeViolationsWithPercentageScale.

    rules_configuration = "commented_out_rules"
