"""Jacoco Jenkins plugin coverage report uncovered lines collector."""

from .base import JacocoJenkinsPluginCoverageBaseClass


class JacocoJenkinsPluginUncoveredLines(JacocoJenkinsPluginCoverageBaseClass):
    """Collector for Jacoco Jenkins plugin uncovered lines."""

    coverage_type = "line"
