"""Unit tests for the Bandit security warnings collector."""

import json

from .base import BanditTestCase


class BanditSecurityWarningsTest(BanditTestCase):
    """Unit tests for the security warning metric."""

    METRIC_TYPE = "security_warnings"

    def setUp(self):
        """Extend with test data."""
        super().setUp()
        self.bandit_json = dict(
            results=[
                dict(
                    filename="src/collectors/cxsast.py",
                    issue_confidence="MEDIUM",
                    issue_severity="LOW",
                    issue_text="Possible hardcoded password: '014DF517-39D1-4453-B7B3-9930C563627C'",
                    line_number=37,
                    more_info="https://bandit/b106_hardcoded_password_funcarg.html",
                    test_id="B106",
                    test_name="hardcoded_password_funcarg",
                )
            ]
        )
        self.expected_entities = [
            dict(
                key="B106:src-collectors-cxsast_py:37",
                location="src/collectors/cxsast.py:37",
                issue_text="Possible hardcoded password: '014DF517-39D1-4453-B7B3-9930C563627C'",
                issue_severity="Low",
                issue_confidence="Medium",
                more_info="https://bandit/b106_hardcoded_password_funcarg.html",
            )
        ]

    async def test_warnings(self):
        """Test the number of security warnings."""
        response = await self.collect(self.metric, get_request_json_return_value=self.bandit_json)
        self.assert_measurement(response, value="1", entities=self.expected_entities)

    async def test_warnings_with_high_severity(self):
        """Test the number of high severity security warnings."""
        self.set_source_parameter("severities", ["high"])
        response = await self.collect(self.metric, get_request_json_return_value=self.bandit_json)
        self.assert_measurement(response, value="0", entities=[])

    async def test_warnings_with_high_confidence(self):
        """Test the number of high confidence security warnings."""
        self.set_source_parameter("confidence_levels", ["high"])
        response = await self.collect(self.metric, get_request_json_return_value=self.bandit_json)
        self.assert_measurement(response, value="0", entities=[])

    async def test_zipped_report(self):
        """Test that a zip with reports can be read."""
        self.set_source_parameter("url", "bandit.zip")
        zipfile = self.zipped_report(*[(f"bandit{index}.json", json.dumps(self.bandit_json)) for index in range(2)])
        response = await self.collect(self.metric, get_request_content=zipfile)
        self.assert_measurement(response, value="2", entities=self.expected_entities + self.expected_entities)

    async def test_report_in_gitlab(self):
        """Test that a private token can be added to the request header for accessing a report in GitLab."""
        self.set_source_parameter("private_token", "token")
        response = await self.collect(self.metric, get_request_json_return_value=self.bandit_json)
        self.assert_measurement(response, value="1", entities=self.expected_entities)
