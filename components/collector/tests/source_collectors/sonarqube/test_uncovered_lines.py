"""Unit tests for the SonarQube uncovered lines collector."""

from .base import SonarQubeTestCase


class SonarQubeUncoveredLinesTest(SonarQubeTestCase):
    """Unit tests for the SonarQube uncovered lines collector."""

    METRIC_TYPE = "uncovered_lines"

    async def test_uncovered_lines(self):
        """Test that the number of uncovered lines and the number of lines to cover are returned."""
        json = dict(
            component=dict(
                measures=[dict(metric="uncovered_lines", value="100"), dict(metric="lines_to_cover", value="1000")]
            )
        )
        response = await self.collect(self.metric, get_request_json_return_value=json)
        self.assert_measurement(
            response, value="100", total="1000", landing_url=self.metric_landing_url.format("uncovered_lines")
        )
