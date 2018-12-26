"""Violation metrics."""

from collector.metric import FewerIsBetterMetric


class Violations(FewerIsBetterMetric):
    """Metric for the number of violations."""

    name = "Number of violations"
    unit = "violations"
