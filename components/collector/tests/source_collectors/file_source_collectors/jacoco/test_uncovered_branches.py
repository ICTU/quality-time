"""Unit tests for the JaCoCo source."""

from .base import JaCoCoCommonCoverageTestsMixin, JaCoCoCommonTestsMixin, JaCoCoTestCase


class JaCoCoUncoveredBranchesTest(JaCoCoCommonCoverageTestsMixin, JaCoCoCommonTestsMixin, JaCoCoTestCase):
    """Unit tests for the JaCoCo metrics."""

    METRIC_TYPE = "uncovered_branches"
    JACOCO_XML = "<report><counter type='BRANCH' missed='2' covered='4'/></report>"

    async def test_uncovered_branches_without_branches(self):
        """Test that a JaCoCo XML without branches results in 100% coverage."""
        response = await self.collect(
            self.metric, get_request_text="<report><counter type='LINE' missed='4' covered='6'/></report>"
        )
        self.assert_measurement(response, value="0", total="0")
