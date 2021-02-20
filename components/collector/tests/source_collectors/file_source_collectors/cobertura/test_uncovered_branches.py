"""Unit tests for the Cobertura uncovered branches collector."""

from .base import CoberturaTestCase, CoberturaCoverageTestsMixin


class CoberturaUncoveredBranchesTest(CoberturaCoverageTestsMixin, CoberturaTestCase):  # skipcq: PTC-W0046
    """Unit tests for the Cobertura uncovered branches collector."""

    COBERTURA_XML = "<coverage branches-covered='6' branches-valid='10' />"
    METRIC_TYPE = "uncovered_branches"
