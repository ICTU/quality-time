"""Test coverage metrics."""

from collector.metric import FewerIsBetterMetric, MoreIsBetterMetric


class CoveredLines(MoreIsBetterMetric):
    """Number of covered lines."""
    name = "Test line coverage"
    unit = "covered lines"


class UncoveredLines(FewerIsBetterMetric):
    """Number of uncovered lines."""
    name = "Test line coverage"
    unit = "uncovered lines"


class CoveredBranches(MoreIsBetterMetric):
    """Number of covered branches."""
    name = "Test branch coverage"
    unit = "covered branches"


class UncoveredBranches(FewerIsBetterMetric):
    """Number of uncovered branches."""
    name = "Test branch coverage"
    unit = "uncovered branches"
