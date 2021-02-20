"""Jacoco coverage report uncovered branches collector."""

from .base import JacocoCoverageBaseClass


class JacocoUncoveredBranches(JacocoCoverageBaseClass):
    """Source class to get the number of uncovered lines from Jacoco XML reports."""

    coverage_type = "branch"
