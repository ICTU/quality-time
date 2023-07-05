"""Unit tests for the SonarQube long units collector."""

from shared_data_model import DATA_MODEL

from .base import SonarQubeTestCase


class SonarQubeLongUnitsTest(SonarQubeTestCase):
    """Unit tests for the SonarQube long units collector."""

    METRIC_TYPE = "long_units"

    async def test_long_units(self):
        """Test that the number of long units is returned."""
        self.set_source_parameter("rules", ["rule1"])
        long_units_json = {"total": "2", "issues": []}
        functions_json = {"component": {"measures": [{"metric": "functions", "value": "4"}]}}
        response = await self.collect(
            get_request_json_side_effect=[
                {},
                long_units_json,
                functions_json,
                long_units_json,
                functions_json,
                long_units_json,
            ],
        )
        expected_rules = ",".join(sorted(DATA_MODEL.sources["sonarqube"].configuration["long_unit_rules"].value))
        self.assert_measurement(
            response,
            value="2",
            total="4",
            landing_url=f"{self.issues_landing_url}&rules={expected_rules}",
        )
