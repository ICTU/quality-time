"""Unit tests for the SonarQube violations collector."""

from .base import SonarQubeTestCase


class SonarQubeViolationsTest(SonarQubeTestCase):
    """Unit tests for the SonarQube violations collector."""

    METRIC_TYPE = "violations"

    async def test_violations(self):
        """Test that the number of violations is returned."""
        json = dict(
            total="2",
            issues=[
                dict(
                    key="violation1",
                    message="message1",
                    component="component1",
                    severity="INFO",
                    type="BUG",
                    creationDate="2020-08-30T22:48:53+0200",
                    updateDate="2020-09-30T22:48:54+0200",
                ),
                dict(
                    key="violation2",
                    message="message2",
                    component="component2",
                    severity="MAJOR",
                    type="CODE_SMELL",
                    creationDate="2019-08-30T21:48:52+0200",
                    updateDate="2019-09-30T21:48:52+0200",
                ),
            ],
        )
        response = await self.collect(get_request_json_return_value=json)
        expected_entities = [
            self.entity(
                key="violation1",
                component="component1",
                entity_type="bug",
                message="message1",
                severity="info",
                creation_date="2020-08-30T22:48:53+0200",
                update_date="2020-09-30T22:48:54+0200",
            ),
            self.entity(
                key="violation2",
                component="component2",
                entity_type="code_smell",
                message="message2",
                severity="major",
                creation_date="2019-08-30T21:48:52+0200",
                update_date="2019-09-30T21:48:52+0200",
            ),
        ]
        self.assert_measurement(response, value="2", entities=expected_entities, landing_url=self.issues_landing_url)
