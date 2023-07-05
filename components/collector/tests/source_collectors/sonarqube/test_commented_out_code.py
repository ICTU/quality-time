"""Unit tests for the SonarQube commented-out code collector."""

from shared_data_model import DATA_MODEL

from .base import SonarQubeTestCase


class SonarQubeCommentedOutCodeTest(SonarQubeTestCase):
    """Unit tests for the SonarQube commented-out code collector."""

    METRIC_TYPE = "commented_out_code"

    async def test_commented_out_code(self):
        """Test that the number of lines with commented out code is returned."""
        json = {"total": "2"}
        response = await self.collect(get_request_json_return_value=json)
        expected_rules = ",".join(sorted(DATA_MODEL.sources["sonarqube"].configuration["commented_out_rules"].value))
        self.assert_measurement(
            response,
            value="2",
            total="100",
            landing_url=f"{self.issues_landing_url}&rules={expected_rules}",
        )
