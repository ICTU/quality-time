"""Cobertura coverage report uncovered lines collector."""

from .base import CoberturaCoverageBaseClass


class CoberturaUncoveredLines(CoberturaCoverageBaseClass):
    """Source class to get the number of uncovered lines from Cobertura XML reports."""

    coverage_type = "lines"
