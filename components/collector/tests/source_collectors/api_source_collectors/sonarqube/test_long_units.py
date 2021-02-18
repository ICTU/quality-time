"""Unit tests for the SonarQube long units collector."""

from .base import SonarQubeTestCase


class SonarQubeLongUnitsTest(SonarQubeTestCase):
    """Unit tests for the SonarQube long units collector."""

    METRIC_TYPE = "long_units"

    async def test_long_units(self):
        """Test that the number of long units is returned."""
        self.sources["source_id"]["parameters"]["rules"] = ["rule1"]
        long_units_json = dict(total="2", issues=[])
        functions_json = dict(component=dict(measures=[dict(metric="functions", value="4")]))
        response = await self.collect(
            self.metric,
            get_request_json_side_effect=[
                {},
                long_units_json,
                functions_json,
                long_units_json,
                functions_json,
                long_units_json,
            ],
        )
        self.assert_measurement(
            response,
            value="2",
            total="4",
            landing_url=f"{self.issues_landing_url}&rules=abap:S104,c:FileLoc,cpp:FileLoc,csharpsquid:S104,"
            "csharpsquid:S138,flex:S138,go:S104,go:S138,javascript:S104,javascript:S138,kotlin:S104,"
            "kotlin:S138,objc:FileLoc,php:S104,php:S138,php:S2042,Pylint:R0915,python:S104,ruby:S104,"
            "ruby:S138,scala:S104,scala:S138,squid:S00104,squid:S1188,squid:S138,java:S138,squid:S2972,"
            "swift:S104,typescript:S104,typescript:S138,vbnet:S104,vbnet:S138,Web:FileLengthCheck,"
            "Web:LongJavaScriptCheck",
        )
