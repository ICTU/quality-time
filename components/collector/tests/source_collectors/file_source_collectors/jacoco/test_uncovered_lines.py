"""Unit tests for the JaCoCo source."""

from .base import JaCoCoCommonCoverageTestsMixin, JaCoCoCommonTestsMixin, JaCoCoTestCase


class JaCoCoUncoveredLinesTest(JaCoCoCommonCoverageTestsMixin, JaCoCoCommonTestsMixin, JaCoCoTestCase):
    """Unit tests for the JaCoCo metrics."""

    METRIC_TYPE = "uncovered_lines"
    JACOCO_XML = "<report><counter type='LINE' missed='2' covered='4'/></report>"
