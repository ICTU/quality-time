"""Cobertura coverage report uncovered branches collector."""

from .base import CoberturaCoverageBaseClass


class CoberturaUncoveredBranches(CoberturaCoverageBaseClass):
    """Source class to get the number of uncovered lines from Cobertura XML reports."""

    coverage_type = "branches"
