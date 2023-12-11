"""Unit tests for the SonarQube complex units collector."""

from .base import SonarQubeTestCase


class SonarQubeComplexUnitsTest(SonarQubeTestCase):
    """Unit tests for the SonarQube complex units collector."""

    METRIC_TYPE = "complex_units"

    async def test_complex_units(self):
        """Test that the number of complex units are returned."""
        complex_units_json = {"total": "2"}
        functions_json = {"component": {"measures": [{"metric": "functions", "value": "4"}]}}
        response = await self.collect(
            get_request_json_side_effect=[
                {},
                complex_units_json,
                functions_json,
                complex_units_json,
                functions_json,
                complex_units_json,
            ],
        )
        self.assert_measurement(
            response,
            value="2",
            total="4",
            landing_url=f"{self.issues_landing_url}&rules={self.sonar_rules("complex_unit")}",
        )
