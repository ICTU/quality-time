"""Unit tests for the Anchore security warnings collector."""

import json

from shared.utils.functions import md5_hash

from .base import AnchoreTestCase


class AnchoreSecurityWarningsTest(AnchoreTestCase):
    """Unit tests for the security warning metric."""

    METRIC_TYPE = "security_warnings"

    def create_entity(
        self, cve: str, package: str, fix: str = "None", severity: str = "Low", filename: str = ""
    ) -> dict[str, str]:
        """Return an expected entity."""
        return {
            "key": md5_hash(f"{filename}{cve}:{package}"),
            "filename": filename,
            "cve": cve,
            "url": self.url,
            "fix": fix,
            "severity": severity,
            "package": package,
        }

    async def test_warnings(self):
        """Test the number of security warnings."""
        self.set_source_parameter("severities", ["Low"])
        response = await self.collect(get_request_json_return_value=self.vulnerabilities_json)
        expected_entities = [self.create_entity("CVE-000", "package")]
        self.assert_measurement(response, value="1", entities=expected_entities)

    async def test_filter_by_fix_availability(self):
        """Test the security warnings can be filtered by fix availability."""
        self.set_source_parameter("fix_availability", ["fix available"])
        response = await self.collect(get_request_json_return_value=self.vulnerabilities_json)
        expected_entities = [self.create_entity("CVE-000", package="package2", fix="v1.2.3", severity="Unknown")]
        self.assert_measurement(response, value="1", entities=expected_entities)

    async def test_zipped_report(self):
        """Test that a zip with reports can be read."""
        self.set_source_parameter("severities", ["Low"])
        self.set_source_parameter("url", "anchore.zip")
        filename = "vuln.json"
        zipfile = self.zipped_report(
            (filename, json.dumps(self.vulnerabilities_json)),
            ("details.json", json.dumps(self.details_json)),
        )
        response = await self.collect(get_request_content=zipfile)
        expected_entities = [self.create_entity("CVE-000", "package", filename=filename)]
        self.assert_measurement(response, value="1", entities=expected_entities)
