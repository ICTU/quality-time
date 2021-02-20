"""Unit tests for the SonarQube many parameters collector."""

from .base import SonarQubeTestCase


class SonarQubeManyParametersTest(SonarQubeTestCase):
    """Unit tests for the SonarQube many parameters collector."""

    METRIC_TYPE = "many_parameters"

    async def test_many_parameters(self):
        """Test that the number of functions with too many parameters is returned."""
        self.set_source_parameter("rules", ["rule1"])
        many_parameters_json = dict(total="2", issues=[])
        functions_json = dict(component=dict(measures=[dict(metric="functions", value="4")]))
        response = await self.collect(
            get_request_json_side_effect=[
                {},
                many_parameters_json,
                functions_json,
                many_parameters_json,
                functions_json,
                many_parameters_json,
            ]
        )
        self.assert_measurement(
            response,
            value="2",
            total="4",
            landing_url=f"{self.issues_landing_url}&rules=c:S107,csharpsquid:S107,csharpsquid:S2436,cpp:S107,flex:S107,"
            "javascript:ExcessiveParameterList,javascript:S107,objc:S107,php:S107,"
            "plsql:PlSql.FunctionAndProcedureExcessiveParameters,python:S107,squid:S00107,java:S107,"
            "tsql:S107,typescript:S107",
        )
