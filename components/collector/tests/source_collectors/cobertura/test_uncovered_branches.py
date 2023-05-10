"""Unit tests for the Cobertura uncovered branches collector."""

from .base import CoberturaCoverageTestsMixin, CoberturaTestCase


class CoberturaUncoveredBranchesTest(CoberturaCoverageTestsMixin, CoberturaTestCase):
    """Unit tests for the Cobertura uncovered branches collector."""

    COBERTURA_XML = "<coverage branches-covered='6' branches-valid='10' />"
    METRIC_TYPE = "uncovered_branches"
