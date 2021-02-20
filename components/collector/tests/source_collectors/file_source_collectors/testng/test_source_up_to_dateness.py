"""Unit tests for the JUnit XML test report source."""

from datetime import datetime

from .base import TestNGCollectorTestCase


class TestNGSourceUpToDatenessTest(TestNGCollectorTestCase):
    """Unit tests for the source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        xml = """<?xml version="1.0"?>
            <testng-results skipped="0" failed="0" ignored="0" total="1" passed="1">
              <suite name="testMethod" started-at="2020-09-06T19:02:59Z" finished-at="2020-09-06T19:45:45Z"/>
            </testng-results>"""
        response = await self.collect(self.metric, get_request_text=xml)
        expected_age = (datetime.utcnow() - datetime(2020, 9, 6, 19, 45, 45)).days
        self.assert_measurement(response, value=str(expected_age))
