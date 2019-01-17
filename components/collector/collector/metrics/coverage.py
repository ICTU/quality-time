"""Test coverage metrics."""

from collector.metric import Metric


class CoveredLines(Metric):
    """Number of covered lines."""


class UncoveredLines(Metric):
    """Number of uncovered lines."""


class CoveredBranches(Metric):
    """Number of covered branches."""


class UncoveredBranches(Metric):
    """Number of uncovered branches."""
