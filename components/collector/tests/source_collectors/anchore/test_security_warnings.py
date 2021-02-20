"""Unit tests for the Anchore security warnings collector."""

import json

from collector_utilities.functions import md5_hash

from .base import AnchoreTestCase


class AnchoreSecurityWarningsTest(AnchoreTestCase):
    """Unit tests for the security warning metric."""

    METRIC_TYPE = "security_warnings"

    async def test_warnings(self):
        """Test the number of security warnings."""
        response = await self.collect(get_request_json_return_value=self.vulnerabilities_json)
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
        self.set_source_parameter("url", "anchore.zip")
        filename = "vuln.json"
        zipfile = self.zipped_report(
            (filename, json.dumps(self.vulnerabilities_json)), ("details.json", json.dumps(self.details_json))
        )
        response = await self.collect(get_request_content=zipfile)
        expected_entities = [
            dict(
                key=md5_hash(f"{filename}CVE-000:package"),
                filename=filename,
                cve="CVE-000",
                url=self.url,
                fix="None",
                severity="Low",
                package="package",
            )
        ]
        self.assert_measurement(response, value="1", entities=expected_entities)
