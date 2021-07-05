"""Unit tests for the SonarQube suppressed violations collector."""

from .base import SonarQubeTestCase


class SonarQubeSuppressedViolationsTest(SonarQubeTestCase):
    """Unit tests for the SonarQube suppressed violations collector."""

    METRIC_TYPE = "suppressed_violations"

    async def test_suppressed_violations(self):
        """Test that the number of suppressed violations includes both suppressed issues as well as suppressed rules."""
        violations_json = dict(
            total="1",
            issues=[
                dict(
                    key="violation1",
                    message="message1",
                    component="component1",
                    severity="INFO",
                    type="BUG",
                    creationDate="2020-07-30T22:48:52+0200",
                    updateDate="2020-09-30T21:48:52+0200",
                )
            ],
        )
        wont_fix_json = dict(
            total="1",
            issues=[
                dict(
                    key="violation2",
                    message="message2",
                    component="component2",
                    severity="MAJOR",
                    type="CODE_SMELL",
                    resolution="WONTFIX",
                    creationDate="2019-08-15:48:52+0200",
                    updateDate="2019-09-30T20:48:52+0200",
                )
            ],
        )
        total_violations_json = dict(total="4")
        response = await self.collect(
            get_request_json_side_effect=[{}, violations_json, wont_fix_json, total_violations_json]
        )
        expected_entities = [
            self.entity(
                key="violation1",
                component="component1",
                entity_type="bug",
                message="message1",
                severity="info",
                resolution="",
                creation_date="2020-07-30T22:48:52+0200",
                update_date="2020-09-30T21:48:52+0200",
            ),
            self.entity(
                key="violation2",
                component="component2",
                entity_type="code_smell",
                message="message2",
                severity="major",
                resolution="won't fix",
                creation_date="2019-08-15:48:52+0200",
                update_date="2019-09-30T20:48:52+0200",
            ),
        ]
        self.assert_measurement(
            response,
            value="2",
            total="4",
            entities=expected_entities,
            landing_url=f"{self.issues_landing_url}&rules=csharpsquid:S1309,php:NoSonar,Pylint:I0011,Pylint:I0020,"
            "squid:NoSonar,java:NoSonar,squid:S1309,java:S1309,squid:S1310,"
            "java:S1310,squid:S1315,java:S1315",
        )
