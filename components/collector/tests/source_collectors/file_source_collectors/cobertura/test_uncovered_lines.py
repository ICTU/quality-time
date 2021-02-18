"""Unit tests for the Cobertura uncovered lines collector."""

from .base import CoberturaTestCase, CoberturaCoverageTestsMixin


class CoberturaUncoveredLinesTest(CoberturaCoverageTestsMixin, CoberturaTestCase):
    """Unit tests for the Cobertura uncovered lines collector."""

    COBERTURA_XML = "<coverage lines-covered='6' lines-valid='10' />"
    METRIC_TYPE = "uncovered_lines"
