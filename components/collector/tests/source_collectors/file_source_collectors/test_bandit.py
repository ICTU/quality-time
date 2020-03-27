"""Unit tests for the Bandit source."""

import io
import json
import zipfile
from datetime import datetime, timezone

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class BanditTestCase(SourceCollectorTestCase):
    """Base class for testing Bandit collectors."""

    def setUp(self):
        super().setUp()
        self.sources = dict(source_id=dict(type="bandit", parameters=dict(url="bandit.json")))


class BanditSecurityWarningsTest(BanditTestCase):
    """Unit tests for the security warning metric."""

    def setUp(self):
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
                    test_name="hardcoded_password_funcarg")])
        self.metric = dict(type="security_warnings", sources=self.sources, addition="sum")
        self.expected_entities = [
            dict(
                location="src/collectors/cxsast.py:37", key="B106:src/collectors/cxsast.py:37",
                issue_text="Possible hardcoded password: '014DF517-39D1-4453-B7B3-9930C563627C'",
                issue_severity="Low", issue_confidence="Medium",
                more_info="https://bandit/b106_hardcoded_password_funcarg.html")]

    async def test_warnings(self):
        """Test the number of security warnings."""
        response = await self.collect(self.metric, get_request_json_return_value=self.bandit_json)
        self.assert_measurement(response, value="1", entities=self.expected_entities)

    async def test_warnings_with_high_severity(self):
        """Test the number of high severity security warnings."""
        self.sources["source_id"]["parameters"]["severities"] = ["high"]
        response = await self.collect(self.metric, get_request_json_return_value=self.bandit_json)
        self.assert_measurement(response, value="0", entities=[])

    async def test_warnings_with_high_confidence(self):
        """Test the number of high confidence security warnings."""
        self.sources["source_id"]["parameters"]["confidence_levels"] = ["high"]
        response = await self.collect(self.metric, get_request_json_return_value=self.bandit_json)
        self.assert_measurement(response, value="0", entities=[])

    async def test_zipped_report(self):
        """Test that a zip with reports can be read."""
        self.sources["source_id"]["parameters"]["url"] = "bandit.zip"
        bytes_io = io.BytesIO()
        with zipfile.ZipFile(bytes_io, mode="w") as zipped_bandit_report:
            zipped_bandit_report.writestr(
                "bandit.json", json.dumps(self.bandit_json))
        response = await self.collect(self.metric, get_request_content=bytes_io.getvalue())
        self.assert_measurement(response, value="1", entities=self.expected_entities)

    async def test_report_in_gitlab(self):
        """Test that a private token can be added to the request header for accessing a report in GitLab."""
        self.sources["source_id"]["parameters"]["private_token"] = "token"
        response = await self.collect(self.metric, get_request_json_return_value=self.bandit_json)
        self.assert_measurement(response, value="1", entities=self.expected_entities)


class BanditSourceUpToDatenessTest(BanditTestCase):
    """Unit tests for the source up to dateness metric."""

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        metric = dict(type="source_up_to_dateness", sources=self.sources, addition="max")
        bandit_json = dict(generated_at="2019-07-12T07:38:47Z")
        response = await self.collect(metric, get_request_json_return_value=bandit_json)
        expected_age = (datetime.now(tz=timezone.utc) - datetime(2019, 7, 12, 7, 38, 47, tzinfo=timezone.utc)).days
        self.assert_measurement(response, value=str(expected_age))
