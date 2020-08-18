"""Unit tests for the Snyk source."""

import io
import json
import zipfile
from datetime import datetime, timezone

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class SnykTestCase(SourceCollectorTestCase):
    """Base class for Snyk unit tests."""

    def setUp(self):
        self.sources = dict(
            source_id=dict(
                type="snyk",
                parameters=dict(url="snyk-vuln.json", details_url="snyk-details.json", severities=["Low"])))
        self.vulnerabilities_json = dict(
            vulnerabilities=[
                dict(
                    [('key', 'be5b4bb76e44441465100337df9337eb'),
                     ('title', 'Cross Site Scripting'),
                     ('id', 'VULN-TEST'),
                     ('severity', 'Low'),
                     ('fixedIn', '3.0'),
                     ('packageName', 'vulnerablepackage'),
                     ('version', '1.0'),
                     ('from', [
        "mainpackage@0.0.0",
        "vulnerablepackage@1.2.0"
      ])]
                )
            ])
        self.details_json = [dict(analyzed_at="2020-02-07T22:53:43Z")]


class SnykSecurityWarningsTest(SnykTestCase):
    """Unit tests for the security warning metric."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="security_warnings", sources=self.sources, addition="sum")
        self.expected_entities = [
            dict(
                [('key', 'be5b4bb76e44441465100337df9337eb'),
                 ('cve', 'Cross Site Scripting'),
                 ('url', 'https://snyk.io/vuln/VULN-TEST'),
                 ('severity', 'Low'),
                 ('fix', '3.0'),
                 ('package', 'vulnerablepackage'),
                 ('version', '1.0'),
                 ('package_include', "vulnerablepackage@1.2.0"
      )]
                )
        ]

    async def test_warnings(self):
        """Test the number of security warnings."""
        response = await self.collect(self.metric, get_request_json_return_value=self.vulnerabilities_json)
        self.assert_measurement(response, value="1", entities=self.expected_entities)


class SnykSourceUpToDatenessTest(SnykTestCase):
    """Unit tests for the source up to dateness metric."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="source_up_to_dateness", sources=self.sources, addition="max")
        self.expected_age = (datetime.now(tz=timezone.utc) - datetime(2020, 2, 7, 22, 53, 43, tzinfo=timezone.utc)).days

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        response = await self.collect(self.metric, get_request_json_return_value=self.details_json)
        self.assert_measurement(response, value=str(self.expected_age))