"""Unit tests for the SonarQube suppressed violations collector."""

from .base import SonarQubeTestCase


class SonarQubeSuppressedViolationsTest(SonarQubeTestCase):
    """Unit tests for the SonarQube suppressed violations collector."""

    METRIC_TYPE = "suppressed_violations"

    async def test_suppressed_violations(self):
        """Test that the number of suppressed violations includes both suppressed issues as well as suppressed rules."""
        violations_json = {
            "total": "1",
            "issues": [
                {
                    "key": "violation1",
                    "message": "message1",
                    "component": "component1",
                    "severity": "INFO",
                    "type": "BUG",
                    "creationDate": "2020-07-30T22:48:52+0200",
                    "updateDate": "2020-09-30T21:48:52+0200",
                },
            ],
        }
        wont_fix_json = {
            "total": "1",
            "issues": [
                {
                    "key": "violation2",
                    "message": "message2",
                    "component": "component2",
                    "severity": "MAJOR",
                    "type": "CODE_SMELL",
                    "resolution": "WONTFIX",
                    "creationDate": "2019-08-15:50:52+0200",
                    "updateDate": "2019-09-30T20:50:52+0200",
                },
            ],
        }
        total_violations_json = {"total": "4"}
        response = await self.collect(
            get_request_json_side_effect=[{}, violations_json, wont_fix_json, total_violations_json],
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
                creation_date="2019-08-15:50:52+0200",
                update_date="2019-09-30T20:50:52+0200",
            ),
        ]
        self.assert_measurement(
            response,
            value="2",
            total="4",
            entities=expected_entities,
            landing_url="https://sonarqube/project/issues?id=id&branch=master",
        )

    async def test_suppressed_with_rationale_violations(self):
        """Test that the number of suppressed violations includes both suppressed issues as well as suppressed rules."""
        wont_fix_rationale_json = {
            "total": "1",
            "issues": [
                {
                    "key": "violation3",
                    "message": "message3",
                    "component": "component1",
                    "severity": "MAJOR",
                    "type": "CODE_SMELL",
                    "resolution": "WONTFIX",
                    "comments": [
                        {
                            "login": "test-user",
                            "htmlText": "<strong>TEST</strong>",
                            "markdown": "*TEST*",
                            "createdAt": "2023-04-12T08:04:02+0000",
                        },
                        {
                            "login": "test-user",
                            "htmlText": "comment2",
                            "markdown": "comment2",
                            "createdAt": "2023-04-12T09:04:38+0000",
                        },
                    ],
                    "creationDate": "2019-08-15:52:52+0200",
                    "updateDate": "2019-09-30T20:52:52+0200",
                },
            ],
        }
        total_violations_json = {"total": "1"}
        response = await self.collect(
            get_request_json_side_effect=[{}, {}, wont_fix_rationale_json, total_violations_json],
        )
        expected_entities = [
            self.entity(
                key="violation3",
                component="component1",
                entity_type="code_smell",
                message="message3",
                severity="major",
                resolution="won't fix",
                rationale="test-user: *TEST*\ntest-user: comment2",
                creation_date="2019-08-15:52:52+0200",
                update_date="2019-09-30T20:52:52+0200",
            ),
        ]
        self.assert_measurement(
            response,
            value="1",
            total="1",
            entities=expected_entities,
            landing_url="https://sonarqube/project/issues?id=id&branch=master",
        )
