"""Unit tests for the JUnit XML test report source."""

import io
import zipfile
from datetime import datetime

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class TestNGCollectorTestCase(SourceCollectorTestCase):
    """Base class for TestNG collector unit tests."""

    def setUp(self):
        super().setUp()
        self.url = "https://testng.xml"
        self.sources = dict(source_id=dict(type="testng", parameters=dict(url=self.url)))


class TestNGTestReportTest(TestNGCollectorTestCase):
    """Unit tests for the TestNG XML test report metrics."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="tests", sources=self.sources, addition="sum")
        self.testng_xml = """<testng-results skipped="0" failed="1" ignored="1" total="3" passed="1">
          <suite name="suite1" started-at="2020-09-06T19:02:59Z" finished-at="2020-09-06T19:45:45Z">
            <test name="test1" started-at="2020-09-06T19:02:59Z" finished-at="2020-09-06T19:45:45Z">
              <class name="class1">
                <test-method status="PASS" name="method1" is-config="true" started-at="2020-09-06T19:28:40Z" 
                  finished-at="2020-09-06T19:28:40Z">
                </test-method>
                <test-method status="PASS" name="method2" started-at="2020-09-06T19:28:40Z" 
                  finished-at="2020-09-06T19:29:04Z">
                </test-method> 
                <test-method status="FAIL" name="method3" started-at="2020-09-06T19:28:40Z" 
                  finished-at="2020-09-06T19:29:04Z">
                </test-method> 
              </class>
            </test>
          </suite>
        </testng-results>
        """

    async def test_tests(self):
        """Test that the number of tests is returned."""
        response = await self.collect(self.metric, get_request_text=self.testng_xml)
        self.assert_measurement(response, value="3", total="3")

    async def test_failed_tests(self):
        """Test that the failed tests are returned."""
        self.sources["source_id"]["parameters"]["test_result"] = ["failed"]
        response = await self.collect(self.metric, get_request_text=self.testng_xml)
        self.assert_measurement(response, value="1", total="3")

    async def test_zipped_testng_report(self):
        """Test that the number of tests is returned from a zip with TestNG reports."""
        self.sources["source_id"]["parameters"]["url"] = "testng.zip"
        bytes_io = io.BytesIO()
        with zipfile.ZipFile(bytes_io, mode="w") as zipped_testng_report:
            zipped_testng_report.writestr("testng.xml", self.testng_xml)
        response = await self.collect(self.metric, get_request_content=bytes_io.getvalue())
        self.assert_measurement(response, value="3", total="3")


class TestNGSourceUpToDatenessTest(TestNGCollectorTestCase):
    """Unit tests for the source up-to-dateness metric."""

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        metric = dict(type="source_up_to_dateness", sources=self.sources, addition="max")
        response = await self.collect(
            metric, get_request_text="""<?xml version="1.0"?>
            <testng-results skipped="0" failed="0" ignored="0" total="1" passed="1">
              <suite name="testMethod" started-at="2020-09-06T19:02:59Z" finished-at="2020-09-06T19:45:45Z"/>
            </testng-results>""")
        expected_age = (datetime.utcnow() - datetime(2020, 9, 6, 19, 45, 45)).days
        self.assert_measurement(response, value=str(expected_age))
