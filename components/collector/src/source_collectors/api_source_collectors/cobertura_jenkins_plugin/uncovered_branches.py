"""Cobertura Jenkins plugin coverage report uncovered lines collector."""

from .base import CoberturaJenkinsPluginCoverageBaseClass


class CoberturaJenkinsPluginUncoveredBranches(CoberturaJenkinsPluginCoverageBaseClass):
    """Collector for Cobertura Jenkins plugin uncovered branches."""

    coverage_type = "conditionals"
