"""Jacoco Jenkins plugin coverage report uncovered branches collector."""

from .base import JacocoJenkinsPluginCoverageBaseClass


class JacocoJenkinsPluginUncoveredBranches(JacocoJenkinsPluginCoverageBaseClass):
    """Collector for Jacoco Jenkins plugin uncovered branches."""

    coverage_type = "branch"
