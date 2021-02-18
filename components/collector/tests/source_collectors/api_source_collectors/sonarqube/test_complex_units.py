"""Unit tests for the SonarQube complex units collector."""

from .base import SonarQubeTestCase


class SonarQubeComplexUnitsTest(SonarQubeTestCase):
    """Unit tests for the SonarQube complex units collector."""

    METRIC_TYPE = "complex_units"

    async def test_complex_units(self):
        """Test that the number of complex units are returned."""
        complex_units_json = dict(total="2")
        functions_json = dict(component=dict(measures=[dict(metric="functions", value="4")]))
        response = await self.collect(
            self.metric,
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
            landing_url=f"{self.issues_landing_url}&rules=csharpsquid:S1541,csharpsquid:S3776,flex:FunctionComplexity,"
            "javascript:FunctionComplexity,javascript:S1541,javascript:S3776,go:S3776,kotlin:S3776,"
            "php:S1541,php:S3776,python:FunctionComplexity,python:S3776,ruby:S3776,scala:S3776,"
            "squid:MethodCyclomaticComplexity,java:S1541,squid:S3776,typescript:S1541,typescript:S3776,"
            "vbnet:S1541,vbnet:S3776",
        )
