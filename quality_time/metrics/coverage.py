"""Test coverage metrics."""

from quality_time.metric import FewerIsBetterMetric, MoreIsBetterMetric


class CoveredLines(MoreIsBetterMetric):
    """Number of covered lines."""
    unit = "covered lines"


class UncoveredLines(FewerIsBetterMetric):
    """Number of uncovered lines."""
    unit = "uncovered lines"


class CoveredBranches(MoreIsBetterMetric):
    """Number of covered branches."""
    unit = "covered branches"


class UncoveredBranches(FewerIsBetterMetric):
    """Number of uncovered branches."""
    unit = "uncovered branches"
