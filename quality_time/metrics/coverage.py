"""Test coverage metrics."""

from quality_time.metric import FewerIsBetterMetric, MoreIsBetterMetric


class CoveredLines(MoreIsBetterMetric):
    """Number of covered lines."""


class UncoveredLines(FewerIsBetterMetric):
    """Number of uncovered lines."""


class CoveredBranches(MoreIsBetterMetric):
    """Number of covered lines."""


class UncoveredBranches(FewerIsBetterMetric):
    """Number of uncovered lines."""
