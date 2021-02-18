"""Unit tests for the SonarQube duplicated lines collector."""

from .base import SonarQubeTestCase


class SonarQubeDuplicatedLinesTest(SonarQubeTestCase):
    """Unit tests for the SonarQube duplicated lines collector."""

    METRIC_TYPE = "duplicated_lines"

    async def test_duplicated_lines(self):
        """Test that the number of duplicated lines and the total number of lines are returned."""
        json = dict(
            component=dict(measures=[dict(metric="duplicated_lines", value="10"), dict(metric="lines", value="100")])
        )
        response = await self.collect(self.metric, get_request_json_return_value=json)
        self.assert_measurement(
            response, value="10", total="100", landing_url=self.metric_landing_url.format("duplicated_lines")
        )
