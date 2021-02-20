"""Jacoco coverage report uncovered lines collector."""

from .base import JacocoCoverageBaseClass


class JacocoUncoveredLines(JacocoCoverageBaseClass):
    """Source class to get the number of uncovered lines from Jacoco XML reports."""

    coverage_type = "line"
