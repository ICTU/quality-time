"""Unit tests for the SonarQube duplicated lines collector."""

from .base import SonarQubeTestCase


class SonarQubeDuplicatedLinesTest(SonarQubeTestCase):
    """Unit tests for the SonarQube duplicated lines collector."""

    async def test_uncovered_branches(self):
        """Test that the number of uncovered branches and the number of branches to cover are returned."""
        json = dict(
            component=dict(
                measures=[
                    dict(metric="uncovered_conditions", value="10"),
                    dict(metric="conditions_to_cover", value="200"),
                ]
            )
        )
        metric = dict(type="uncovered_branches", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(
            response, value="10", total="200", landing_url=self.metric_landing_url.format("uncovered_conditions")
        )
