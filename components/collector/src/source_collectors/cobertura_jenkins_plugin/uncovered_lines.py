"""Cobertura Jenkins plugin coverage report uncovered lines collector."""

from .base import CoberturaJenkinsPluginCoverageBaseClass


class CoberturaJenkinsPluginUncoveredLines(CoberturaJenkinsPluginCoverageBaseClass):
    """Collector for Cobertura Jenkins plugin uncovered lines."""

    coverage_type = "lines"
