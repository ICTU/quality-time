"""Unit tests for the Anchore source."""

import io
import json
import zipfile
from datetime import datetime, timezone

from collector_utilities.functions import md5_hash

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class AnchoreTestCase(SourceCollectorTestCase):
    """Base class for Anchore unit tests."""

    def setUp(self):
        """Extend to set up Anchore fixtures."""
        super().setUp()
        self.url = "https://cve"
        self.sources = dict(
            source_id=dict(
                type="anchore",
                parameters=dict(url="image-vuln.json", details_url="image-details.json", severities=["Low"]),
            )
        )
        self.vulnerabilities_json = dict(
            vulnerabilities=[
                dict(vuln="CVE-000", package="package", fix="None", url=self.url, severity="Low"),
                dict(vuln="CVE-000", package="package2", fix="None", url=self.url, severity="Unknown"),
            ]
        )
        self.details_json = [dict(analyzed_at="2020-02-07T22:53:43Z")]


class AnchoreSecurityWarningsTest(AnchoreTestCase):
    """Unit tests for the security warning metric."""

    def setUp(self):
        """Extend to set up security warning fixtures."""
        super().setUp()
        self.metric = dict(type="security_warnings", sources=self.sources, addition="sum")

    async def test_warnings(self):
        """Test the number of security warnings."""
        response = await self.collect(self.metric, get_request_json_return_value=self.vulnerabilities_json)
        expected_entities = [
            dict(
                key=md5_hash("CVE-000:package"),
                filename="",
                cve="CVE-000",
                url=self.url,
                fix="None",
                severity="Low",
                package="package",
            )
        ]
        self.assert_measurement(response, value="1", entities=expected_entities)

    async def test_zipped_report(self):
        """Test that a zip with reports can be read."""
        self.sources["source_id"]["parameters"]["url"] = "anchore.zip"
        bytes_io = io.BytesIO()
        with zipfile.ZipFile(bytes_io, mode="w") as zipped_anchore_report:
            zipped_anchore_report.writestr("vuln.json", json.dumps(self.vulnerabilities_json))
            zipped_anchore_report.writestr("details.json", json.dumps(self.details_json))
        response = await self.collect(self.metric, get_request_content=bytes_io.getvalue())
        expected_entities = [
            dict(
                key=md5_hash("vuln.jsonCVE-000:package"),
                filename="vuln.json",
                cve="CVE-000",
                url=self.url,
                fix="None",
                severity="Low",
                package="package",
            )
        ]
        self.assert_measurement(response, value="1", entities=expected_entities)


class AnchoreSourceUpToDatenessTest(AnchoreTestCase):
    """Unit tests for the source up to dateness metric."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="source_up_to_dateness", sources=self.sources, addition="max")
        self.expected_age = (datetime.now(tz=timezone.utc) - datetime(2020, 2, 7, 22, 53, 43, tzinfo=timezone.utc)).days

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        response = await self.collect(self.metric, get_request_json_return_value=self.details_json)
        self.assert_measurement(response, value=str(self.expected_age))

    async def test_zipped_report(self):
        """Test that a zip with reports can be read."""
        self.sources["source_id"]["parameters"]["details_url"] = "anchore.zip"
        bytes_io = io.BytesIO()
        with zipfile.ZipFile(bytes_io, mode="w") as zipped_anchore_report:
            zipped_anchore_report.writestr("vuln.json", json.dumps(self.vulnerabilities_json))
            zipped_anchore_report.writestr("details.json", json.dumps(self.details_json))
        response = await self.collect(self.metric, get_request_content=bytes_io.getvalue())
        self.assert_measurement(response, value=str(self.expected_age))
