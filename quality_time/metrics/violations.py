"""Violation metrics."""

from quality_time.metric import FewerIsBetterMetric


class Violations(FewerIsBetterMetric):
    """Metric for the number of violations."""
    unit = "violations"
