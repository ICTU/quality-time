"""Unit tests for the SonarQube uncovered branches collector."""

from .base import SonarQubeTestCase


class SonarQubeUncoveredBranchesTest(SonarQubeTestCase):
    """Unit tests for the SonarQube uncovered branches collector."""

    METRIC_TYPE = "uncovered_branches"

    async def test_uncovered_branches(self):
        """Test that the number of uncovered branches and the number of branches to cover are returned."""
        json = {
            "component": {
                "measures": [
                    {"metric": "uncovered_conditions", "value": "10"},
                    {"metric": "conditions_to_cover", "value": "200"},
                ],
            },
        }
        response = await self.collect(get_request_json_return_value=json)
        self.assert_measurement(
            response,
            value="10",
            total="200",
            landing_url=self.metric_landing_url.format("uncovered_conditions"),
        )

    async def test_missing_uncovered_branches(self):
        """Test that the number of (uncovered) branches are assumed to be 0 when missing."""
        json = {"component": {"measures": []}}
        response = await self.collect(get_request_json_return_value=json)
        self.assert_measurement(
            response,
            value="0",
            total="100",
            landing_url=self.metric_landing_url.format("uncovered_conditions"),
        )
